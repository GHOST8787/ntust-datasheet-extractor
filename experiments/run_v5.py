"""V5 strict schema experiment driver — single cell.

Cell G: GPT-4o x Conservative x Multimodal x **Pydantic JSON Schema strict mode**

Compares against V4 Cell E (GPT-4o x Conservative x Multimodal x json_object = 79.1%).
Only variable: response_format json_object -> json_schema strict.

Usage:
    python -u "C:\\Users\\sunny\\Desktop\\2025_NTUST\\20260508_qimoxiezye\\run_v5.py"
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
    "use_strict_schema": "1",
    "log": "v5_run_gpt4o_con_multimodal_strict.log",
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    print(
        f"[V5] BACKEND={CELL['backend']} CRITIC_PROMPT_MODE={CELL['mode']} "
        f"PDF_EXTRACTOR={CELL['extractor']} USE_STRICT_SCHEMA={CELL['use_strict_schema']}",
        flush=True,
    )
    t0 = time.time()

    env = os.environ.copy()
    env["BACKEND"] = CELL["backend"]
    env["CRITIC_PROMPT_MODE"] = CELL["mode"]
    env["PDF_EXTRACTOR"] = CELL["extractor"]
    env["USE_STRICT_SCHEMA"] = CELL["use_strict_schema"]

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
    print(f"[V5] {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)  ->  {CELL['log']}", flush=True)


if __name__ == "__main__":
    main()
