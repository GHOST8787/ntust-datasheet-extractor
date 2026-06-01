"""檢查每顆 datasheet 的尺寸頁:是向量線條(get_drawings 多)還是嵌入點陣圖(大 image)。
決定「用 PDF 向量結構判方向」這條路走不走得通。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import fitz
import config
import crop_extractor

ORIG = list(crop_extractor.CROP_ANCHOR_KEYWORDS)


def find_dim_page(pdf):
    crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG
    bb = crop_extractor.find_anchor_bboxes(pdf)
    if not bb:
        crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG + ["DIMENSIONS", "Dimensions"]
        bb = crop_extractor.find_anchor_bboxes(pdf)
        crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG
    return bb[0][0] if bb else None


print("每顆尺寸頁:向量線條數 / 嵌入點陣圖數(及最大圖尺寸)\n", flush=True)
for pn, fn in config.PART_TO_PDF.items():
    pdf = config.DATASHEETS_DIR / fn
    doc = fitz.open(str(pdf))
    pg = find_dim_page(pdf)
    if pg is None:
        # fallback: drawings 最多的頁
        pg = max(range(min(doc.page_count, 8)), key=lambda i: len(doc[i].get_drawings()))
        note = "(無anchor,取drawings最多頁)"
    else:
        note = ""
    page = doc[pg]
    nd = len(page.get_drawings())
    imgs = page.get_images(full=True)
    ni = len(imgs)
    max_img = ""
    if imgs:
        dims = []
        for im in imgs:
            xref = im[0]
            try:
                info = doc.extract_image(xref)
                dims.append((info["width"], info["height"]))
            except Exception:
                pass
        if dims:
            w, h = max(dims, key=lambda d: d[0] * d[1])
            max_img = f"最大圖 {w}x{h}px"
    verdict = "向量" if nd >= 20 else ("點陣" if ni and not nd else "?")
    print(f"[{pn}] p{pg+1}{note}: 向量線條={nd}  點陣圖={ni}  {max_img}  → {verdict}", flush=True)
    doc.close()
