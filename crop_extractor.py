"""V21+ crop 工具：在 PDF 內找 Package Outline / Mechanical Drawing 文字附近的 bbox，
crop 該區塊高 zoom 重新光柵化，給 LLM 看「特定區塊」而非整頁。

不依賴 train set 內容 — 純 generic PDF 結構處理。
"""
import base64
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass


CROP_ANCHOR_KEYWORDS = [
    "Package Outline",
    "Mechanical Drawing",
    "Mechanical Dimensions",
    "Package Dimensions",
    "Body Dimensions",
    "Outline Drawing",
]

# crop bbox 從 anchor 文字往外擴展的範圍（單位 PDF point，1 point = 1/72 inch）
# 整張 A4 約 595 x 842 points。表格 + 圖通常 200-400 points 寬高
ANCHOR_EXPAND_UP = 50
ANCHOR_EXPAND_DOWN = 400
ANCHOR_EXPAND_LEFT = 50
ANCHOR_EXPAND_RIGHT = 500


def find_anchor_bboxes(pdf_path: Path, max_pages: int = 10) -> List[Tuple[int, Tuple[float, float, float, float]]]:
    """掃 PDF 找 anchor 文字的 bbox，回傳 [(page_idx_0based, bbox), ...]
    bbox 是 (x0, y0, x1, y1)，已擴展到含表格的範圍。
    """
    import fitz
    out = []
    doc = fitz.open(str(pdf_path))
    try:
        for idx in range(min(doc.page_count, max_pages)):
            page = doc[idx]
            page_rect = page.rect
            for kw in CROP_ANCHOR_KEYWORDS:
                rects = page.search_for(kw)
                for r in rects:
                    expanded = (
                        max(0, r.x0 - ANCHOR_EXPAND_LEFT),
                        max(0, r.y0 - ANCHOR_EXPAND_UP),
                        min(page_rect.width, r.x1 + ANCHOR_EXPAND_RIGHT),
                        min(page_rect.height, r.y1 + ANCHOR_EXPAND_DOWN),
                    )
                    out.append((idx, expanded))
                    break  # 同關鍵字同頁只取第一個 hit
    finally:
        doc.close()
    return out


def crop_to_base64(pdf_path: Path, page_idx: int, bbox: Tuple[float, float, float, float], zoom: float = 5.0) -> str:
    """對指定頁 + bbox crop 高 zoom，回 base64 PNG"""
    import fitz
    doc = fitz.open(str(pdf_path))
    try:
        page = doc[page_idx]
        mat = fitz.Matrix(zoom, zoom)
        clip = fitz.Rect(*bbox)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        return base64.b64encode(pix.tobytes("png")).decode("ascii")
    finally:
        doc.close()


def get_dimension_crops(pdf_path: Path, zoom: float = 5.0, max_crops: int = 3) -> List[Tuple[int, str]]:
    """主要入口：對 PDF 找 dimension anchor 區塊 crop 出來。
    回傳 [(page_1based, base64_png), ...]，最多 max_crops 張。
    """
    bboxes = find_anchor_bboxes(pdf_path)
    crops = []
    seen_pages = set()
    for page_idx, bbox in bboxes:
        if page_idx in seen_pages:
            continue
        try:
            b64 = crop_to_base64(pdf_path, page_idx, bbox, zoom=zoom)
            crops.append((page_idx + 1, b64))
            seen_pages.add(page_idx)
        except Exception as e:
            print(f"  [crop fail] page {page_idx + 1}: {e}", flush=True)
        if len(crops) >= max_crops:
            break
    return crops


if __name__ == "__main__":
    # smoke test：對一顆 train PDF 跑看看
    import config
    test_pdf = config.DATASHEETS_DIR / "BAV99W_datasheet_en_20171221.pdf"
    if test_pdf.exists():
        crops = get_dimension_crops(test_pdf)
        print(f"Found {len(crops)} dimension crops")
        for page, b64 in crops:
            print(f"  page {page}: {len(b64)} chars base64")
    else:
        print(f"Test PDF missing: {test_pdf}")
