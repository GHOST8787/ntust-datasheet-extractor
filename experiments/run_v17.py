"""V17 雙重驗證 driver — temperature 0.5 試打破 systematic 視覺錯誤

V17 基於 V12 配置（當前最佳）+ LLM_TEMPERATURE=0.5：
- V12-V16 都 temperature=0 deterministic
- LLM 看圖判斷錯多半是 systematic（同樣 prompt 同樣 image → 同樣錯）
- 提高 temperature 讓 LLM 有機會換視角

風險：temperature 變化可能引入 noise 反而降低其他欄位準確度。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V17-orig", "script": "main.py",             "log": "v17_run_original_10.log"},
    {"id": "V17-new",  "script": "extract_new_pdfs.py", "log": "v17_run_new_5.log"},
]

BASE_ENV = {
    "BACKEND": "azure_gpt4o",
    "CRITIC_PROMPT_MODE": "conservative",  # 回 V12 baseline
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "USE_MULTIMODAL_CRITIC": "0",          # 撤 V14-V16 multimodal critic
    "LLM_TEMPERATURE": "0.5",              # V17 新加（既有變數）
    "VERSION_LABEL": "v17",
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
    print(f"V17 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
