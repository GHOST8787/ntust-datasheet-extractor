"""V7 driver — 跑兩個換維度子實驗：

  V7 J: GPT-4o × Conservative × Multimodal_TOC（TOC-based 精準截圖定位）
  V7 L: Mistral × Conservative × Multimodal（Mistral vision 試跑）

V7 K（容差重評估）走另一條獨立 reevaluate.py。
V7 M（GPT-4.1-mini）等 Sunny 開 deployment 後另外跑。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELLS = [
    {
        "id": "V7 J",
        "backend": "azure_gpt4o",
        "extractor": "multimodal_toc",
        "mode": "conservative",
        "use_strict": "0",
        "use_cot": "0",
        "log": "v7_j_run_gpt4o_con_multimodaltoc.log",
    },
    {
        "id": "V7 L",
        "backend": "azure_mistral",
        "extractor": "multimodal",
        "mode": "conservative",
        "use_strict": "0",
        "use_cot": "0",
        "log": "v7_l_run_mistral_con_multimodal.log",
    },
]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    total = len(CELLS)
    overall_start = time.time()

    for i, cell in enumerate(CELLS, 1):
        print(f"[{i}/{total}] {cell['id']}  BACKEND={cell['backend']} EXTRACTOR={cell['extractor']}", flush=True)
        t0 = time.time()

        env = os.environ.copy()
        env["BACKEND"] = cell["backend"]
        env["CRITIC_PROMPT_MODE"] = cell["mode"]
        env["PDF_EXTRACTOR"] = cell["extractor"]
        env["USE_STRICT_SCHEMA"] = cell["use_strict"]
        env["USE_CHAIN_OF_THOUGHT"] = cell["use_cot"]

        log_path = WORK_DIR / cell["log"]
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
        print(f"[{i}/{total}] {cell['id']} {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)  ->  {cell['log']}", flush=True)

    total_elapsed = time.time() - overall_start
    print(f"V7 J+L done in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
