"""V3 2x2 dual-agent experiment driver — pure Python (avoids PowerShell + Chinese path encoding hell).

Cells:
  1. Mistral medium + conservative critic
  2. GPT-4o + strict critic
  3. GPT-4o + conservative critic
(Mistral + strict already done = 68.2%, archive renamed *_strict, not re-running)

Run from anywhere:
    python -u "C:\\Users\\sunny\\Desktop\\2025_NTUST\\20260508_qimoxiezye\\run_2x2.py"

Or just place this file in WORK_DIR and run from there.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"backend": "azure_mistral", "mode": "conservative", "log": "v3_run_mistral_conservative.log"},
    {"backend": "azure_gpt4o",   "mode": "strict",       "log": "v3_run_gpt4o_strict.log"},
    {"backend": "azure_gpt4o",   "mode": "conservative", "log": "v3_run_gpt4o_conservative.log"},
]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    total = len(CELLS)
    overall_start = time.time()

    for i, cell in enumerate(CELLS, 1):
        backend = cell["backend"]
        mode = cell["mode"]
        log_name = cell["log"]
        log_path = WORK_DIR / log_name

        print(f"[{i}/{total}] BACKEND={backend} CRITIC_PROMPT_MODE={mode} ... ", flush=True)
        t0 = time.time()

        env = os.environ.copy()
        env["BACKEND"] = backend
        env["CRITIC_PROMPT_MODE"] = mode

        # main.py uses load_dotenv() with default override=False, so env vars set
        # before subprocess start will WIN over .env settings.
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
        print(f"[{i}/{total}] {status} in {elapsed:.1f}s  →  {log_name}", flush=True)

    total_elapsed = time.time() - overall_start
    print(f"All {total} cells finished in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
