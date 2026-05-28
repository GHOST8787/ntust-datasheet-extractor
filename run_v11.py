"""V11 雙重驗證 driver — 精準補「Max 欄定位 + 變體禁用」

V11 改動（基於 V10）：
1. 步驟 3 強化：取 Max 欄（最右邊），禁止取 Min / Nom 欄，含 explicit FFSH5065B 範例
2. 步驟 3.5 加：禁用變體符號（A1/A2/E1/E2/D1/D2/L/L1/H/H1/H_E/b/c/e/Q/S/P）當 L/W/H
3. 明寫「L 是 lead length，不是 body Length」
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V11-orig", "script": "main.py",             "log": "v11_run_original_10.log"},
    {"id": "V11-new",  "script": "extract_new_pdfs.py", "log": "v11_run_new_5.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "VERSION_LABEL": "v11",
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
    print(f"V11 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
