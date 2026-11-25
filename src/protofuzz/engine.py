"""Fuzzing orchestration, result tracking, crash corpus and resumable state."""
from __future__ import annotations
import json, random, hashlib
from pathlib import Path
from datetime import datetime, timezone
from .mutators import MUTATORS, dictionary_mutation
from .network import send_tcp, heartbeat

DEFAULT_WORDS = [b"PING", b"HELLO", b"VERSION", b"CRASH", b"STATUS", b"\x00", b"\xff"]

class FuzzEngine:
    def __init__(self, host, port, seed, iterations, timeout, output_dir,
                 heartbeat_message=b"PING\n", dictionary=None, start_at=1, seed_value=7):
        self.host, self.port, self.seed = host, int(port), seed
        self.iterations, self.timeout = int(iterations), float(timeout)
        self.output_dir = Path(output_dir)
        self.corpus_dir = self.output_dir / "corpus"
        self.heartbeat_message = heartbeat_message
        self.dictionary = dictionary or DEFAULT_WORDS
        self.start_at = max(1, int(start_at))
        self.rng = random.Random(seed_value)
        self.results = []
        self.crashes = []

    def run(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        strategies = list(MUTATORS)
        for iteration in range(self.start_at, self.start_at + self.iterations):
            strategy = self.rng.choice(strategies + ["dictionary"])
            if strategy == "dictionary":
                mutated = dictionary_mutation(self.seed, self.rng, self.dictionary)
            else:
                mutated = MUTATORS[strategy](self.seed, self.rng)
            sent = send_tcp(self.host, self.port, mutated, self.timeout)
            alive = heartbeat(self.host, self.port, self.heartbeat_message, self.timeout)
            crashed = not alive
            digest = hashlib.sha256(mutated).hexdigest()
            item = {
                "iteration": iteration, "strategy": strategy,
                "input_hex": mutated.hex(), "input_sha256": digest,
                "send_status": sent["status"], "response_text": sent["response_text"],
                "response_hex": sent["response_hex"], "send_error": sent["error"],
                "heartbeat_alive": alive, "crash_detected": crashed,
                "timestamp_utc": datetime.now(timezone.utc).isoformat()
            }
            self.results.append(item)
            if crashed:
                path = self.corpus_dir / f"crash_{iteration:06d}_{digest[:10]}.bin"
                path.write_bytes(mutated)
                item["corpus_file"] = str(path)
                self.crashes.append(item)
            print(f"[{iteration}] {strategy:<16} send={sent['status']:<16} "
                  f"heartbeat={'ALIVE' if alive else 'FAILED'}")
            if crashed:
                print(f"    [!] Crash/hang suspected; saved: {item['corpus_file']}")
                print("    [i] Stopping this run because the lab service is not responding.")
                break
        return self.build_report()

    def build_report(self):
        report = {
            "tool": "ProtoFuzz", "version": "1.0.0",
            "target": {"host": self.host, "port": self.port},
            "configuration": {"iterations_requested": self.iterations,
                              "start_iteration": self.start_at, "timeout_seconds": self.timeout},
            "summary": {"iterations_completed": len(self.results),
                        "crashes_detected": len(self.crashes),
                        "responses_received": sum(r["send_status"] == "ok" for r in self.results),
                        "timeouts_or_errors": sum(r["send_status"] != "ok" for r in self.results)},
            "results": self.results,
            "crashes": self.crashes
        }
        json_path = self.output_dir / "report.json"
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        text_path = self.output_dir / "report.txt"
        lines = [
            "PROTOFUZZ RUN REPORT", "=" * 60,
            f"Target: {self.host}:{self.port}",
            f"Iterations completed: {len(self.results)}",
            f"Crashes detected: {len(self.crashes)}",
            f"Responses received: {report['summary']['responses_received']}",
            f"Timeouts/errors: {report['summary']['timeouts_or_errors']}",
            "", "CRASH CORPUS:"
        ]
        lines += [f"- Iteration {c['iteration']}: {c.get('corpus_file', 'not saved')}" for c in self.crashes]
        if not self.crashes:
            lines.append("- No heartbeat failures detected.")
        text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        state = {"last_completed_iteration": self.results[-1]["iteration"] if self.results else self.start_at - 1}
        (self.output_dir / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        return report
