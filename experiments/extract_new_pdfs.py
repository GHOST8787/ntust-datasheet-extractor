"""V4 E 配置對「網路隨機抓的 5 份 datasheet」跑抽取（無 ground truth）。

目的：驗證原 10 顆達 79.1% 的 V4 E 配置能不能 generalize 到新 datasheet。
特別關注：
  - validators.py L/W/H 範圍 0.2~15mm 對大封裝（TO-247 等）的影響
  - PIN {2,3,4,8} 限定對 IC / 大功率封裝的影響
  - prompt 內 SMD 二極體合理範圍 0.8~10mm 對大封裝的影響

不算分數（沒 ground truth），只輸出 raw extracted JSON 給人工驗證。
"""
import json
import os
import sys
import time
from pathlib import Path

# 強制 V4 E 配置
os.environ["BACKEND"] = "azure_gpt4o"
os.environ["CRITIC_PROMPT_MODE"] = "conservative"
os.environ["PDF_EXTRACTOR"] = "multimodal"
os.environ["USE_STRICT_SCHEMA"] = "0"
os.environ["USE_CHAIN_OF_THOUGHT"] = "0"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

import config
from llm_backend import get_backend
from pdf_extractor import get_pdf_extractor, MultiModalExtractor
from validators import validate_and_fix
from main import run_dual_agent_loop
from iteration_logger import IterationLogger


NEW_PDFS = [
    ("FFSH5065B",     r"C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\AA\FFSH5065B-F085-D.PDF"),
    ("FFSD1065B",     r"C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\AA\FFSD1065B-D.PDF"),
    ("VS3C20ET07T",   r"C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\AA\vs-3c20et07t-m3.pdf"),
    ("VS3C12ET07S2L", r"C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\AA\vs-3c12et07s2l-m.pdf"),
    ("ASA006V065F4",  r"C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\AA\ASA006V065F4.pdf"),
]


def main():
    backend = get_backend()
    extractor = get_pdf_extractor()
    multimodal = isinstance(extractor, MultiModalExtractor)
    # cell_id 由環境變數 VERSION_LABEL 控制（V8 設 "v8"）
    version = os.environ.get("VERSION_LABEL", "v4_E").lower()
    cell_id = f"{version}_NEW_PDFS_test"

    print(f"[backend]      {backend.name}")
    print(f"[pdf extractor] {extractor.name}")
    print(f"[multimodal]    {multimodal}")
    print(f"[cell id]       {cell_id}")
    print()

    logger = IterationLogger(config.OUTPUT_DIR / "iteration_logs", cell_id)
    out: dict = {}
    overall_t0 = time.time()

    for pn, pdf_str in NEW_PDFS:
        pdf_path = Path(pdf_str)
        if not pdf_path.exists():
            print(f"      [WARN] {pn}: 找不到 {pdf_path.name}")
            out[pn] = {"_error": "PDF not found"}
            continue
        print(f"  - {pn}", flush=True)
        logger.start_part(pn)
        try:
            t0 = time.time()
            pdf_text, images_b64, image_pages = extractor.extract_with_images(pdf_path)
            pdf_ms = int((time.time() - t0) * 1000)
            logger.log_pdf_extract(
                extractor_name=extractor.name,
                text_chars=len(pdf_text),
                num_images=len(images_b64),
                elapsed_ms=pdf_ms,
                image_pages=image_pages,
            )
            print(f"        [pdf] {len(pdf_text)} chars + {len(images_b64)} images (pages {image_pages})", flush=True)

            answer, history = run_dual_agent_loop(
                backend, pn, pdf_text,
                logger=logger,
                images_b64=images_b64,
                multimodal=True,
            )
            out[pn] = answer
            out[pn]["_history"] = history
        except Exception as e:
            print(f"        [ERROR] {type(e).__name__}: {e}", flush=True)
            out[pn] = {"_error": f"{type(e).__name__}: {e}"}
            try:
                logger.log_error(str(e))
            except Exception:
                pass

    logger.close()

    # 寫 raw 結果
    out_path = config.OUTPUT_DIR / "new_pdfs_extracted.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print()
    print(f"Wrote: {out_path}")
    print(f"Total time: {time.time() - overall_t0:.1f}s")

    # 印出每顆抽到的關鍵欄位給人類速看
    print()
    print("=" * 80)
    print("抽到的關鍵欄位（給人工驗證用）")
    print("=" * 80)
    KEY_FIELDS = [
        "Maximum Length (mm)",
        "Maximum Width (mm)",
        "Maximum Height (mm)",
        "PIN Number",
        "I_O、I_F (A)",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)",
    ]
    for pn, rec in out.items():
        print(f"\n[{pn}]")
        if "_error" in rec:
            print(f"  ERROR: {rec['_error']}")
            continue
        for f in KEY_FIELDS:
            print(f"  {f:<48}: {rec.get(f)}")


if __name__ == "__main__":
    main()
