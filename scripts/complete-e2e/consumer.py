#!/usr/bin/env python3
"""Live grok-build proofs: cargo metadata, scoped cargo test/check, SOURCE_REV, CLI help."""
from __future__ import annotations
import json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def step(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    extra = f" — {detail}" if detail else ""
    print(f"  {status}  {name}{extra}", flush=True)


def write_junit(fails: int) -> None:
    junit_dir = Path(
        os.environ.get("HURC_COMPLETE_E2E_JUNIT")
        or (ROOT / ".hurc-harness/state/complete-e2e/junit")
    )
    junit_dir.mkdir(parents=True, exist_ok=True)
    if fails:
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<testsuite name="grok-build-consumer" tests="1" failures="{fails}" errors="0">\n'
            '  <testcase classname="grok-build" name="consumer">\n'
            '    <failure message="consumer failed"/>\n'
            '  </testcase>\n'
            '</testsuite>\n'
        )
    else:
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuite name="grok-build-consumer" tests="1" failures="0" errors="0">\n'
            '  <testcase classname="grok-build" name="consumer"/>\n'
            '</testsuite>\n'
        )
    (junit_dir / "grok-build-consumer.xml").write_text(body)


def main() -> int:
    print("grok-build consumer proofs (Rust CLI/TUI — no PHPUnit)", flush=True)
    fails = 0
    env = os.environ.copy()
    # Avoid rust-toolchain download without rustup; host cargo 1.85 works for small crates.
    env.pop("RUSTUP_TOOLCHAIN", None)

    # 1) cargo metadata workspace integrity
    t0 = time.time()
    r = subprocess.run(
        ["cargo", "metadata", "--no-deps", "--format-version", "1"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    ok = r.returncode == 0
    n_pkg = 0
    has_pager = False
    has_version = False
    if ok:
        try:
            meta = json.loads(r.stdout)
            names = {p.get("name") for p in meta.get("packages") or []}
            n_pkg = len(names)
            has_pager = "xai-grok-pager-bin" in names
            has_version = "xai-grok-version" in names
            ok = n_pkg >= 10 and has_pager and has_version
        except Exception as e:
            ok = False
            r = type("R", (), {"stderr": str(e), "stdout": "", "returncode": 1})()
    detail = f"packages={n_pkg} pager={has_pager} version={has_version} elapsed={time.time()-t0:.1f}s"
    if not ok:
        detail += " " + ((r.stderr or r.stdout or "")[-200:].replace("\n", " "))
    step("cargo metadata workspace", ok, detail)
    if not ok:
        fails += 1

    # 2) cargo test -p xai-grok-version (real unit test)
    t0 = time.time()
    r = subprocess.run(
        ["cargo", "test", "-p", "xai-grok-version", "--", "--nocapture"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    out = (r.stdout or "") + (r.stderr or "")
    ok = r.returncode == 0 and "test result: ok" in out
    step("cargo test -p xai-grok-version", ok, f"elapsed={time.time()-t0:.1f}s rc={r.returncode}")
    if not ok:
        fails += 1
        print(out[-400:], flush=True)

    # 3) cargo check -p xai-grok-version
    t0 = time.time()
    r = subprocess.run(
        ["cargo", "check", "-p", "xai-grok-version"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    ok = r.returncode == 0
    step("cargo check -p xai-grok-version", ok, f"elapsed={time.time()-t0:.1f}s")
    if not ok:
        fails += 1
        print((r.stderr or r.stdout or "")[-300:], flush=True)

    # 4) SOURCE_REV integrity
    rev = ROOT / "SOURCE_REV"
    ok = rev.is_file()
    detail = "missing"
    if ok:
        text = rev.read_text().strip()
        ok = bool(re.fullmatch(r"[0-9a-f]{40}", text))
        detail = text[:12] + "…" if ok else f"bad={text!r}"
    step("SOURCE_REV sha40", ok, detail)
    if not ok:
        fails += 1

    # 5) Cargo.toml names TUI binary crate
    cargo_toml = (ROOT / "Cargo.toml").read_text(errors="replace")
    ok = "xai-grok-pager-bin" in cargo_toml and "[workspace]" in cargo_toml
    step("Cargo.toml workspace members include pager-bin", ok)
    if not ok:
        fails += 1

    # 6) README documents install / build
    readme = (ROOT / "README.md").read_text(errors="replace")
    ok = "Grok Build" in readme and ("cargo" in readme.lower() or "x.ai/cli" in readme)
    step("README product docs", ok, f"bytes={len(readme)}")
    if not ok:
        fails += 1

    write_junit(fails)
    return 1 if fails else 0


if __name__ == "__main__":
    _argv = set(sys.argv[1:])
    if _argv & {"-h", "--help"}:
        print("Usage: consumer.py [--help] [--version]")
        print("  Live grok-build proofs: cargo metadata/test/check, SOURCE_REV, README")
        print("options:")
        print("  -h, --help     show this help")
        print("  -V, --version  print version")
        raise SystemExit(0)
    if _argv & {"-V", "--version"}:
        print("grok-build-consumer 1.0.0")
        raise SystemExit(0)
    if _argv:
        print("unrecognized arguments:", " ".join(sys.argv[1:]), file=sys.stderr)
        print("Usage: consumer.py [--help] [--version]", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())
