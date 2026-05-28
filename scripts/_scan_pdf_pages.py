"""掃描 10 份 PDF，每份找哪幾頁含 mechanical / package keywords。

目的：驗證假設 — 是否有元件的「真正 Package Dimensions 頁」在 V4 _MAX_IMAGES=3 範圍外。
"""
import sys
from pathlib import Path

import fitz  # PyMuPDF

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

DATASHEETS = Path(r"C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\datasheets")

# 精準關鍵字（高信心 = body dimensions）vs 模糊關鍵字（可能是 footprint）
PRECISE_BODY = ["package outline", "package dimensions", "mechanical drawing", "mechanical dimensions", "body dimensions", "outline drawing"]
FOOTPRINT = ["land pattern", "solder pad", "footprint", "recommended"]

PDFS = [
    "1N4148W N0571 REV.E.pdf",
    "BAS16.pdf",
    "BAS21HT1-D.pdf",
    "BAT750.pdf",
    "BAV99W_datasheet_en_20171221.pdf",
    "CD4148WTP.pdf",
    "DFLS160.pdf",
    "MBR15U150(TO-277).pdf",
    "MSB30M.pdf",
    "SBR05U20LPS.pdf",
]


def scan(pdf_path: Path):
    doc = fitz.open(str(pdf_path))
    body_pages = []
    fp_pages = []
    try:
        for i, page in enumerate(doc):
            text = (page.get_text() or "").lower()
            for kw in PRECISE_BODY:
                if kw in text:
                    body_pages.append((i + 1, kw))
                    break
            for kw in FOOTPRINT:
                if kw in text:
                    fp_pages.append((i + 1, kw))
                    break
        total = doc.page_count
    finally:
        doc.close()
    return total, body_pages, fp_pages


print(f"{'PDF':<40} {'Pages':>5}  Body Dimensions (page, kw)        Footprint (page, kw)")
print("-" * 120)

for fname in PDFS:
    p = DATASHEETS / fname
    if not p.exists():
        print(f"{fname:<40} MISSING")
        continue
    total, body, fp = scan(p)
    body_str = ", ".join(f"p{pg}({kw[:14]})" for pg, kw in body) or "-"
    fp_str = ", ".join(f"p{pg}({kw[:14]})" for pg, kw in fp) or "-"

    # 標出：body 頁是否在前 5 頁內（V4 _MAX_IMAGES=3 + 鄰頁可達 ~5）
    body_max_page = max((pg for pg, _ in body), default=0)
    flag = "⚠️ BODY>5" if body_max_page > 5 else ""
    flag += "  ⚠️ NO_BODY" if not body else ""

    print(f"{fname:<40} {total:>5}  {body_str:<35}  {fp_str:<30} {flag}")
