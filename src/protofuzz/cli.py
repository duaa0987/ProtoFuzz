from __future__ import annotations
import argparse, sys
from pathlib import Path
from .network import validate_loopback_target, TargetError
from .engine import FuzzEngine, DEFAULT_WORDS

def build_parser():
    parser = argparse.ArgumentParser(prog="protofuzz", description="Educational TCP protocol fuzzer for localhost lab services only.")
    parser.add_argument("--seed", required=True, help="Path to raw seed message file")
    parser.add_argument("--host", default="127.0.0.1", help="Loopback host (default: 127.0.0.1)")
    parser.add_argument("--port", required=True, type=int, help="Local lab TCP port")
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--output", default="reports/run")
    parser.add_argument("--heartbeat", default="PING")
    parser.add_argument("--dictionary")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--start-at", type=int, default=1)
    parser.add_argument("--random-seed", type=int, default=7)
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.iterations < 1 or args.iterations > 10000 or args.timeout <= 0 or args.timeout > 30:
        print("Error: invalid iterations or timeout.", file=sys.stderr); return 2
    seed_path = Path(args.seed)
    if not seed_path.is_file() or not seed_path.read_bytes():
        print(f"Error: seed file missing or empty: {seed_path}", file=sys.stderr); return 2
    try:
        validate_loopback_target(args.host, args.port)
    except TargetError as exc:
        print(f"Target rejected: {exc}", file=sys.stderr); return 2
    seed = seed_path.read_bytes()
    dictionary = DEFAULT_WORDS
    if args.dictionary:
        p = Path(args.dictionary)
        if not p.is_file():
            print(f"Error: dictionary file not found: {p}", file=sys.stderr); return 2
        dictionary = [line.encode() for line in p.read_text(encoding="utf-8").splitlines() if line]
    start_at = args.start_at
    if args.resume:
        import json
        state_path = Path(args.output) / "state.json"
        start_at = json.loads(state_path.read_text()).get("last_completed_iteration", 0) + 1 if state_path.exists() else 1
    print("ProtoFuzz 1.0.0 | LOOPBACK LAB MODE")
    engine = FuzzEngine(args.host, args.port, seed, args.iterations, args.timeout, args.output, args.heartbeat.encode(), dictionary, start_at, args.random_seed)
    report = engine.run()
    print("\nRun complete.")
    print(f"Iterations: {report['summary']['iterations_completed']}")
    print(f"Crash candidates: {report['summary']['crashes_detected']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
