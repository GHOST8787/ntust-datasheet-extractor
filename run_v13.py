"""V13 雙重驗證 driver — 加更強反例（反例 5-8）

V13 改動：反例 5 (DFLS160 類 L/W 視覺互換)
        反例 6 (CD4148WTP 類取保守值)
        反例 7 (MBR15U150 類 W/H 混填)
        反例 8 (BAV99W 類 Tstg 誤當 Min Op Temp)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V13-orig", "script": "main.py",             "log": "v13_run_original_10.log"},
    {"id": "V13-new",  "script": "extract_new_pdfs.py", "log": "v13_run_new_5.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "VERSION_LABEL": "v13",
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    total = len(CELLS)
    overall_start = time.time()

    for i, cell in enumerate(CELLS, 1):
        print(f"[{i}/{total}] {cell['id']}  running {cell['script']}", flush=True)
        t0 = time.time()

        env = os.environ.copy()
        env.update(BASE_ENV)

        log_path = WORK_DIR / cell["log"]
        with open(log_path, "wb") as logf:
            rc = subprocess.run(
                [sys.executable, "-u", cell["script"]],
                cwd=str(WORK_DIR),
                env=env,
                stdout=logf,
                stderr=subprocess.STDOUT,
            ).returncode

        elapsed = time.time() - t0
        status = "OK" if rc == 0 else f"FAIL rc={rc}"
        print(f"[{i}/{total}] {cell['id']} {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)  ->  {cell['log']}", flush=True)

    total_elapsed = time.time() - overall_start
    print(f"V13 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
