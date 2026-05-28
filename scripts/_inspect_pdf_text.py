"""仔細看殘留錯誤 part 的 PDF 文字，找 GT 數字真實出處"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import fitz
import config

PARTS_TO_INSPECT = ["BAV99W", "DFLS160", "MSB30M", "MBR15U150", "BAS16", "BAS21H", "1N4148W"]

for pn in PARTS_TO_INSPECT:
    pdf_fn = config.PART_TO_PDF.get(pn)
    if not pdf_fn:
        continue
    pdf_path = config.DATASHEETS_DIR / pdf_fn
    if not pdf_path.exists():
        continue
    print("=" * 80)
    print(f"# {pn}  ({pdf_fn})")
    print("=" * 80)
    doc = fitz.open(str(pdf_path))
    for idx in range(min(doc.page_count, 6)):
        page = doc[idx]
        text = page.get_text()
        print(f"\n--- Page {idx + 1} ---")
        # 印前 1500 字
        print(text[:1500])
        print(f"... ({len(text)} chars total)")
    doc.close()
    print()
