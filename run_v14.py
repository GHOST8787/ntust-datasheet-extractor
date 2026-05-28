"""V14 雙重驗證 driver — multimodal critic（critic 也看圖）

V14 改動：
1. Revert V13 反例 5-8 回到 V12 prompt
2. Critic 也走 multimodal（USE_MULTIMODAL_CRITIC=1）— 讓 critic 直接驗 L/W/H vs 圖上
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V14-orig", "script": "main.py",             "log": "v14_run_original_10.log"},
    {"id": "V14-new",  "script": "extract_new_pdfs.py", "log": "v14_run_new_5.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "USE_MULTIMODAL_CRITIC": "1",  # V14 新加
    "VERSION_LABEL": "v14",
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
    print(f"V14 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
