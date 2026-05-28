"""V6 Chain-of-Thought multimodal experiment driver — single cell.

Cell H: GPT-4o x Conservative x Multimodal x **Chain-of-Thought (_image_reasoning forced)**

Compares against V4 Cell E (GPT-4o x Con x Multimodal x json_object = 79.1%).
Only variable: chain-of-thought reasoning forced via prompt structure.

NOT using strict schema (V5 showed it hurts on this workload).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent

CELL = {
    "backend": "azure_gpt4o",
    "mode": "conservative",
    "extractor": "multimodal",
    "use_strict_schema": "0",
    "use_chain_of_thought": "1",
    "log": "v6_run_gpt4o_con_multimodal_cot.log",
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    print(
        f"[V6] BACKEND={CELL['backend']} CRITIC_PROMPT_MODE={CELL['mode']} "
        f"PDF_EXTRACTOR={CELL['extractor']} USE_STRICT_SCHEMA={CELL['use_strict_schema']} "
        f"USE_CHAIN_OF_THOUGHT={CELL['use_chain_of_thought']}",
        flush=True,
    )
    t0 = time.time()

    env = os.environ.copy()
    env["BACKEND"] = CELL["backend"]
    env["CRITIC_PROMPT_MODE"] = CELL["mode"]
    env["PDF_EXTRACTOR"] = CELL["extractor"]
    env["USE_STRICT_SCHEMA"] = CELL["use_strict_schema"]
    env["USE_CHAIN_OF_THOUGHT"] = CELL["use_chain_of_thought"]

    log_path = WORK_DIR / CELL["log"]
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
    print(f"[V6] {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)  ->  {CELL['log']}", flush=True)


if __name__ == "__main__":
    main()
