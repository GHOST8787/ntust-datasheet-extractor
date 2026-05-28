"""V8 雙重驗證 driver：

Cell 1: 原 10 顆（同 V4 E 配置 + V8 拔 overfit + 通用化）
        → 對照 V4 E (79.1%) 看 V8 通用化有沒有傷到原樣本分數

Cell 2: 5 顆新 PDF（網路隨機抓）
        → 對照 V4 E 對新 5 顆的 estimated 結果，看 generalize 能拉多少

兩個 cell 都用：
  BACKEND=azure_gpt4o / CRITIC_PROMPT_MODE=conservative
  PDF_EXTRACTOR=multimodal / USE_STRICT_SCHEMA=0 / USE_CHAIN_OF_THOUGHT=0
  VERSION_LABEL=v8（讓 cell_id 用 v8_ 前綴避免覆寫 V4 archive）
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {
        "id": "V8-orig",
        "script": "main.py",
        "log": "v8_run_original_10.log",
    },
    {
        "id": "V8-new",
        "script": "extract_new_pdfs.py",
        "log": "v8_run_new_5.log",
    },
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "VERSION_LABEL": "v8",
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
    print(f"V8 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
