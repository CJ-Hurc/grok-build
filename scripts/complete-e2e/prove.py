#!/usr/bin/env python3
"""grok-build complete-e2e prove wrapper — cargo test/check + structural CLI proofs."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

USAGE = "Usage: prove.py [--help] [--version]\n  wraps scripts/complete-e2e/run.py live product proofs"

def main() -> int:
    a = set(sys.argv[1:])
    if a & {"-h", "--help"}:
        print(USAGE)
        print("options:")
        print("  -h, --help     show this help")
        print("  -V, --version  print version")
        return 0
    if a & {"-V", "--version"}:
        print("grok-build-prove 1.0.0")
        return 0
    if a:
        print("unrecognized arguments:", " ".join(sys.argv[1:]), file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(ROOT / "scripts/complete-e2e/run.py")], cwd=str(ROOT))

if __name__ == "__main__":
    raise SystemExit(main())
