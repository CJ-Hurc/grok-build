#!/usr/bin/env python3
"""Canonical complete-e2e entry for grok-build (Rust CLI/TUI): cargo + structural proofs."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

USAGE = "Usage: run.py [--help] [--version]\n  cargo test/check + SOURCE_REV — no PHPUnit"

def main() -> int:
    print("grok-build complete-e2e")
    print("----------------------------------------")
    rc = 0
    consumer = HERE / "consumer.py"
    r = subprocess.run([sys.executable, str(consumer)], cwd=str(ROOT))
    if r.returncode == 0:
        print("  PASS  consumer complete-e2e", flush=True)
    else:
        print("  FAIL  consumer complete-e2e", flush=True)
        rc = 1
    print("----------------------------------------")
    print("COMPLETE_E2E: PASS" if rc == 0 else "COMPLETE_E2E: FAIL")
    return rc

if __name__ == "__main__":
    _a = set(sys.argv[1:])
    if _a & {"-h", "--help"}:
        print(USAGE)
        print("options:")
        print("  -h, --help     show this help")
        print("  -V, --version  print version")
        raise SystemExit(0)
    if _a & {"-V", "--version"}:
        print("grok-build-complete-e2e 1.0.0")
        raise SystemExit(0)
    if _a:
        print("unrecognized arguments:", " ".join(sys.argv[1:]), file=sys.stderr)
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())
