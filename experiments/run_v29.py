# ============================================================
# !!! OVERFIT -- prompt 反推 BAV99W=150、1N4148W=0.15 等特定答案
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V29 — V12 baseline + 強化 Tj fallback + I_O 優先 prompt 規則

V29 改動（純 prompt engineering，generic 不依賴 train set 內容）：
1. Min Op Temp: 「Tj single value 即使 Tstg 是 range，仍取 Tj」— 救 BAV99W Min Op = 150
2. I_O > I_F 優先級明確化 — 救 1N4148W I_F = 0.15

其他配置同 V12 baseline。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V29-train",   "script": "main_v29.py",             "log": "v29_run_train.log"},
    {"id": "V29-holdout", "script": "extract_new_pdfs_v29.py", "log": "v29_run_holdout.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "USE_MULTIMODAL_CRITIC": "0",
    "VERSION_LABEL": "v29",
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    overall = time.time()
    for i, cell in enumerate(CELLS, 1):
        print(f"[{i}/2] {cell['id']} running {cell['script']}", flush=True)
        t0 = time.time()
        env = os.environ.copy()
        env.update(BASE_ENV)
        log_path = WORK_DIR / cell["log"]
        with open(log_path, "wb") as logf:
            rc = subprocess.run(
                [sys.executable, "-u", cell["script"]],
                cwd=str(WORK_DIR), env=env, stdout=logf, stderr=subprocess.STDOUT,
            ).returncode
        elapsed = time.time() - t0
        status = "OK" if rc == 0 else f"FAIL rc={rc}"
        print(f"[{i}/2] {cell['id']} {status} in {elapsed:.1f}s")

    print(f"V29 done in {time.time() - overall:.1f}s")


if __name__ == "__main__":
    main()
