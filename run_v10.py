"""V10 雙重驗證 driver — 符號對應強化 + 修 V9 副作用

V10 改動（基於 V9）：
1. 步驟 2.5：D/E 符號對應勝過視覺長度（DPAK W>L 是正常的）
2. 步驟 2.6：截圖內有 Package Outline 表 + Land Pattern 圖時，只用 Outline 表
3. L/W/H 只能用 A/D/E 符號 Max 值（禁止 D2/E2/L/L1/H/H_E）
4. V_F/I_R: 「優先 Max，沒 Max 用 Typ 不跳過」修 V9 BAS16 退步副作用
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V10-orig", "script": "main.py",             "log": "v10_run_original_10.log"},
    {"id": "V10-new",  "script": "extract_new_pdfs.py", "log": "v10_run_new_5.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "VERSION_LABEL": "v10",
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
    print(f"V10 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
