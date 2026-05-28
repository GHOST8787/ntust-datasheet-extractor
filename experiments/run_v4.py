"""V4 multimodal experiment driver — single cell.

Cell E: GPT-4o x Conservative critic x Multimodal (text + 3 high-res page images)

Compares against V3 Cell D (GPT-4o x Conservative x text-only = 75.5%).

Usage:
    python -u "C:\\Users\\sunny\\Desktop\\2025_NTUST\\20260508_qimoxiezye\\run_v4.py"
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELL = {
    "backend": "azure_gpt4o",
    "mode": "conservative",
    "extractor": "multimodal",
    "log": "v4_run_gpt4o_con_multimodal.log",
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    print(f"[V4] BACKEND={CELL['backend']} CRITIC_PROMPT_MODE={CELL['mode']} PDF_EXTRACTOR={CELL['extractor']}", flush=True)
    t0 = time.time()

    env = os.environ.copy()
    env["BACKEND"] = CELL["backend"]
    env["CRITIC_PROMPT_MODE"] = CELL["mode"]
    env["PDF_EXTRACTOR"] = CELL["extractor"]

    log_path = WORK_DIR / CELL["log"]
    with open(log_path, "wb") as logf:
        rc = subprocess.run(
            [sys.executable, "-u", "main.py"],
            cwd=str(WORK_DIR),
            env=env,
            stdout=logf,
            stderr=subprocess.STDOUT,
        ).returncode

    elapsed = time.time() - t0
    status = "OK" if rc == 0 else f"FAIL rc={rc}"
    print(f"[V4] {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)  ->  {CELL['log']}", flush=True)


if __name__ == "__main__":
    main()
