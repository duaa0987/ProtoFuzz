# ProtoFuzz

**A Python-based TCP protocol fuzzing tool for controlled localhost testing.**

ProtoFuzz is an educational protocol-testing project. It mutates seed inputs, sends them to a TCP service running on the local machine, monitors the service response, and saves inputs associated with suspected failures for later review.

> **Safety boundary:** ProtoFuzz is intentionally restricted to loopback targets (localhost / 127.0.0.1 / ::1). Use it only with the included demo service or another local service you own and are authorised to test. It is not designed for scanning or testing public systems.

## Features

- Byte-oriented seed mutation strategies
- TCP client for local test services
- Heartbeat-based service health monitoring
- Stops a run when the service becomes unhealthy
- Saves suspected failure inputs to a corpus
- JSON/text reporting
- Unit tests for mutation logic
- Included local demo server

## Project layout

```text
ProtoFuzz/
├── src/protofuzz/       # Core package and command-line interface
├── examples/            # Local demo TCP server and seed inputs
├── tests/               # Unit tests
├── reports/             # Generated reports
├── corpus/              # Saved interesting/failure inputs
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.10 or newer
- Linux (Kali Linux is supported) or another Python-compatible OS

## Run on Kali Linux

1. Extract the downloaded project archive.
2. Open a terminal in the extracted `ProtoFuzz` directory.
3. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install the project:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e .
   ```

5. In terminal 1, start the included local demo server:

   ```bash
   python examples/lab_server.py
   ```

6. In terminal 2, run the CLI help to see available options:

   ```bash
   protofuzz --help
   ```

   Follow the command examples in the packaged project README for the installed CLI options.

7. Run the unit tests:

   ```bash
   python -m pytest -q
   ```

## Safety and responsible use

- Keep tests on localhost and in an isolated lab.
- Do not point the tool at systems you do not own or have explicit permission to test.
- Do not use it for denial-of-service activity or disruption.
- Review generated corpus entries and reports as test artefacts.

## Project resources

- [Complete project ZIP](ProtoFuzz_Complete_Project.zip)
- [Presentation guide (PDF)](docs/ProtoFuzz_Presentation_Guide.pdf)

## Educational purpose

This project demonstrates basic protocol testing concepts: seed inputs, mutation, TCP communication, service-health checks, failure capture, and report generation. It is intended for coursework and controlled learning environments.
