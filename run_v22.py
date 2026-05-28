"""V22 — 改用 multimodal_toc PDF extractor（TOC 結構定位機械頁）

V22 改動：
- PDF_EXTRACTOR=multimodal_toc（而非 multimodal）
- 其他配置同 V12 baseline

PDF TOC 包含 datasheet 目錄結構，命中「Package Outline / Mechanical」章節定位機械頁
比 V8 的 keyword grep 更精準。沒 TOC 的 PDF 自動 fallback 到 keyword grep。

純 generic — 不依賴 train set 內容。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V22-train",   "script": "main.py",             "log": "v22_run_train.log"},
    {"id": "V22-holdout", "script": "extract_new_pdfs.py", "log": "v22_run_holdout.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal_toc",   # ← V22 改這個
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "USE_MULTIMODAL_CRITIC": "0",
    "VERSION_LABEL": "v22",
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
        print(f"[{i}/{total}] {cell['id']} {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)", flush=True)

    print(f"V22 done in {time.time() - overall_start:.1f}s", flush=True)


if __name__ == "__main__":
    main()
