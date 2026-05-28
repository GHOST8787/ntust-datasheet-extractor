"""V18 雙重驗證 driver — 換 Llama-4-Maverick (Meta vision)

V18 改動：
- BACKEND=azure_llama（你 .env 已有 Llama-4-Maverick-17B-128E-Instruct-FP8）
- 其他全等 V12（最佳 baseline）
- Llama 的視覺判斷可能跟 GPT-4o 不同 → 對 DPAK/DFLS160 等 LLM 視覺錯 case 可能有不同結果
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {"id": "V18-orig", "script": "main.py",             "log": "v18_run_original_10.log"},
    {"id": "V18-new",  "script": "extract_new_pdfs.py", "log": "v18_run_new_5.log"},
]

BASE_ENV = {
    "BACKEND": "azure_llama",              # V18 換模型
    "CRITIC_PROMPT_MODE": "conservative",  # V12 baseline
    "PDF_EXTRACTOR": "multimodal",
    "USE_STRICT_SCHEMA": "0",
    "USE_CHAIN_OF_THOUGHT": "0",
    "USE_MULTIMODAL_CRITIC": "0",
    "LLM_TEMPERATURE": "0",
    "VERSION_LABEL": "v18",
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
    print(f"V18 dual validation done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
