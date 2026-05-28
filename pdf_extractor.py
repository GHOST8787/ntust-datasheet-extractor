"""PDF 抽取 backend 抽象層

支援:
  - pdfplumber : 現有 baseline,extract_text + extract_tables(general purpose)
  - fitz       : PyMuPDF,page.get_text + find_tables(general purpose,不同實作)
  - camelot    : camelot-py,專門抽表格(table-specific,需 Ghostscript)
                 narrative text 仍用 pdfplumber 補,因為 camelot 不抽純文字
  - multimodal : V4 加入,基於 fitz 但同時抽純文字 + 機械頁高清截圖（Base64 PNG）
                 給 GPT-4o vision 用,讓 LLM 看圖判斷 L/W/H

由環境變數 PDF_EXTRACTOR 選擇。
"""
import base64
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import config


# ===================================================================
# 抽象介面
# ===================================================================
class PdfExtractor(ABC):
    name: str = "abstract"

    @abstractmethod
    def extract(self, pdf_path: Path) -> str:
        """讀 PDF 回傳完整純文字(已套用頁數截斷與字元上限)"""
        ...

    # ---- 共用工具(子類用)----
    def _join(self, pages: List[Dict]) -> str:
        chunks = []
        for p in pages:
            chunks.append(f"--- Page {p['page_num']} ---")
            chunks.append(p["text"])
            if p.get("tables"):
                chunks.append("\n[Tables]")
                chunks.append(p["tables"])
            chunks.append("")
        return "\n".join(chunks)

    def _truncate(self, pages: List[Dict]) -> str:
        full = self._join(pages)
        if len(full) > config.MAX_PDF_CHARS:
            kw_only = [p for p in pages if p["page_num"] == 1 or p["has_keyword"]]
            full = self._join(kw_only)
            if len(full) > config.MAX_PDF_CHARS:
                full = full[:config.MAX_PDF_CHARS] + "\n... [TRUNCATED]"
        return full

    def _has_keyword(self, text: str, table_text: str) -> bool:
        combined = (text + " " + table_text).lower()
        return any(kw.lower() in combined for kw in config.PDF_KEYWORDS)


# ===================================================================
# 1. pdfplumber(現有 baseline)
# ===================================================================
class PdfPlumberExtractor(PdfExtractor):
    name = "pdfplumber"

    def extract(self, pdf_path: Path) -> str:
        import pdfplumber
        pages: List[Dict] = []
        with pdfplumber.open(pdf_path) as pdf:
            for idx, page in enumerate(pdf.pages):
                if idx >= config.MAX_PDF_PAGES:
                    break
                text = page.extract_text() or ""
                try:
                    tables = page.extract_tables() or []
                except Exception:
                    tables = []
                table_chunks = []
                for tbl in tables:
                    rows = []
                    for row in tbl:
                        cells = [str(c).strip() if c is not None else "" for c in row]
                        rows.append(" | ".join(cells))
                    if rows:
                        table_chunks.append("\n".join(rows))
                tbl_text = "\n\n".join(table_chunks)
                pages.append({
                    "page_num": idx + 1,
                    "text": text,
                    "tables": tbl_text,
                    "has_keyword": self._has_keyword(text, tbl_text),
                })
        return self._truncate(pages)


# ===================================================================
# 2. PyMuPDF / fitz(general purpose 替代實作)
# ===================================================================
class FitzExtractor(PdfExtractor):
    name = "fitz"

    def extract(self, pdf_path: Path) -> str:
        import fitz  # PyMuPDF
        pages: List[Dict] = []
        doc = fitz.open(str(pdf_path))
        try:
            for idx, page in enumerate(doc):
                if idx >= config.MAX_PDF_PAGES:
                    break
                text = page.get_text() or ""
                # PyMuPDF 1.23+ 內建 find_tables
                table_chunks = []
                try:
                    tabs = page.find_tables()
                    for t in tabs.tables:
                        rows = t.extract()
                        row_strs = []
                        for row in rows:
                            cells = [str(c).strip() if c is not None else "" for c in row]
                            row_strs.append(" | ".join(cells))
                        if row_strs:
                            table_chunks.append("\n".join(row_strs))
                except Exception:
                    pass
                tbl_text = "\n\n".join(table_chunks)
                pages.append({
                    "page_num": idx + 1,
                    "text": text,
                    "tables": tbl_text,
                    "has_keyword": self._has_keyword(text, tbl_text),
                })
        finally:
            doc.close()
        return self._truncate(pages)


# ===================================================================
# 3. camelot(table-specific,narrative 仍用 pdfplumber 補)
# ===================================================================
class CamelotExtractor(PdfExtractor):
    name = "camelot"

    def extract(self, pdf_path: Path) -> str:
        import camelot
        import pdfplumber

        # Step 1: pdfplumber 抽 narrative text(camelot 不做這個)
        page_texts: Dict[int, str] = {}
        with pdfplumber.open(pdf_path) as pdf:
            for idx, page in enumerate(pdf.pages):
                if idx >= config.MAX_PDF_PAGES:
                    break
                page_texts[idx + 1] = page.extract_text() or ""

        # Step 2: camelot 抽表格 — 先 lattice(有線框),再 stream(無線框)補
        page_tables: Dict[int, List[str]] = {i: [] for i in page_texts.keys()}
        page_range = f"1-{min(config.MAX_PDF_PAGES, max(page_texts.keys()))}"
        for flavor in ("lattice", "stream"):
            try:
                ts = camelot.read_pdf(str(pdf_path), pages=page_range, flavor=flavor, suppress_stdout=True)
                for t in ts:
                    page_num = t.page
                    df = t.df
                    if df.empty:
                        continue
                    rows = [" | ".join(str(c).strip() for c in row) for row in df.values.tolist()]
                    page_tables.setdefault(page_num, []).append("\n".join(rows))
            except Exception:
                # camelot 偶爾會在某些 PDF 失敗,容錯
                continue

        pages: List[Dict] = []
        for page_num in sorted(page_texts.keys()):
            text = page_texts[page_num]
            tbl_text = "\n\n".join(page_tables.get(page_num, []))
            pages.append({
                "page_num": page_num,
                "text": text,
                "tables": tbl_text,
                "has_keyword": self._has_keyword(text, tbl_text),
            })
        return self._truncate(pages)


# ===================================================================
# 4. multimodal(V4 — fitz 抽純文字 + 機械頁高清截圖 Base64)
# ===================================================================
# V8: 三層關鍵字精準度排序
# 高信心 = 真正的 body dimensions 表（優先選）
_HIGH_PRECISION_KWS = [
    "package outline", "package dimensions",
    "mechanical drawing", "mechanical dimensions",
    "body dimensions", "outline drawing",
]
# 低信心 = footprint / 焊墊（次優先選，因為有時可從焊墊反推 body）
_LOW_PRECISION_KWS = [
    "land pattern", "solder pad", "footprint", "recommended pad",
]
# Fallback 單字（最後選，避免雜訊大）
_FALLBACK_KWS = [
    "package", "mechanical", "outline", "dimensions",
]

# V4 舊變數名留著給 MultiModalTocExtractor fallback 用
_MULTIMODAL_KEYWORDS = _HIGH_PRECISION_KWS + _LOW_PRECISION_KWS + _FALLBACK_KWS

# 上限：V8 拉到 8（V4 是 3，BAV99W 第 5 頁 body 被切過）
_MAX_IMAGES = 8
# 光柵化倍率：V20 從 imlacha V7 的 3.5x 拉到 4.5x（更高解析度給 vision 看尺寸表）
# 可由環境變數 RASTER_ZOOM 覆寫（V20 baseline 改實驗用）
_RASTER_ZOOM = float(os.environ.get("RASTER_ZOOM", "3.5"))


class MultiModalExtractor(PdfExtractor):
    """V4 多模態 extractor：
    - extract(path) 仍回純文字（跟 FitzExtractor 一樣的純文字介面）
    - extract_with_images(path) 多回傳 base64 PNG list + 對應頁碼

    main.py 偵測 isinstance(extractor, MultiModalExtractor) 走 multimodal 路徑。
    """
    name = "multimodal"

    def extract(self, pdf_path: Path) -> str:
        """純文字路徑（讓 critic 沿用同樣文字輸入）"""
        text, _, _ = self._extract_text_and_images(pdf_path)
        return text

    def extract_with_images(
        self, pdf_path: Path
    ) -> Tuple[str, List[str], List[int]]:
        """V4 主要入口：回 (text, base64_images, image_pages_1based)"""
        return self._extract_text_and_images(pdf_path)

    def _extract_text_and_images(
        self, pdf_path: Path
    ) -> Tuple[str, List[str], List[int]]:
        """V8: 三層關鍵字精準度排序 + _MAX_IMAGES=8

        選頁策略：
        1. High precision 頁（含 "Package Outline" / "Mechanical Drawing" 等）優先選滿
        2. 剩餘 quota 給 Low precision 頁（含 "Land Pattern" / "Footprint" 等）
        3. 還有剩 quota 給 Fallback 單字命中頁
        4. 沒任何命中 → 截 PDF 前 _MAX_IMAGES 頁（last resort）
        每層都帶鄰頁擴展（前後各 1 頁）。
        """
        import fitz  # PyMuPDF

        pages_data: List[Dict] = []
        high_hit_pages: List[int] = []
        low_hit_pages: List[int] = []
        fallback_hit_pages: List[int] = []

        doc = fitz.open(str(pdf_path))
        try:
            # ---- Pass 1: 抽純文字 + 三層關鍵字分類 ----
            for idx, page in enumerate(doc):
                if idx >= config.MAX_PDF_PAGES:
                    break
                text = page.get_text() or ""

                table_chunks = []
                try:
                    tabs = page.find_tables()
                    for t in tabs.tables:
                        rows = t.extract()
                        row_strs = []
                        for row in rows:
                            cells = [str(c).strip() if c is not None else "" for c in row]
                            row_strs.append(" | ".join(cells))
                        if row_strs:
                            table_chunks.append("\n".join(row_strs))
                except Exception:
                    pass
                tbl_text = "\n\n".join(table_chunks)

                pages_data.append({
                    "page_num": idx + 1,
                    "text": text,
                    "tables": tbl_text,
                    "has_keyword": self._has_keyword(text, tbl_text),
                })

                lower = (text + " " + tbl_text).lower()
                # 優先檢查 high，再 low，再 fallback（一頁可同時命中多層但分到最高那層）
                if any(kw in lower for kw in _HIGH_PRECISION_KWS):
                    high_hit_pages.append(idx)
                elif any(kw in lower for kw in _LOW_PRECISION_KWS):
                    low_hit_pages.append(idx)
                elif any(kw in lower for kw in _FALLBACK_KWS):
                    fallback_hit_pages.append(idx)

            # ---- 鄰頁擴展 + 按優先層級依序選頁 ----
            def expand_neighbors(pages):
                """加前後鄰頁，回傳 sorted set"""
                out = set()
                for p in pages:
                    out.add(p)
                    if p > 0:
                        out.add(p - 1)
                    if p < doc.page_count - 1 and p + 1 < config.MAX_PDF_PAGES:
                        out.add(p + 1)
                return sorted(out)

            selected = []
            for layer in (
                expand_neighbors(high_hit_pages),
                expand_neighbors(low_hit_pages),
                expand_neighbors(fallback_hit_pages),
            ):
                for p in layer:
                    if p not in selected and len(selected) < _MAX_IMAGES:
                        selected.append(p)
                if len(selected) >= _MAX_IMAGES:
                    break

            # Last resort：完全沒命中 → 截前 _MAX_IMAGES 頁
            if not selected:
                last_resort_max = min(_MAX_IMAGES, doc.page_count, config.MAX_PDF_PAGES)
                selected = list(range(last_resort_max))

            # V20 選頁順序：High precision 頁優先放前面（LLM 對前面 attention 較高）
            # 若 IMAGE_ORDER=precision，按 high → low → fallback 排；其他按頁碼
            image_order = os.environ.get("IMAGE_ORDER", "page").lower()
            if image_order == "precision":
                selected_pages = list(selected)
            else:
                selected_pages = sorted(selected)

            # ---- Pass 2: 光柵化 ----
            images_b64: List[str] = []
            image_pages_1based: List[int] = []
            mat = fitz.Matrix(_RASTER_ZOOM, _RASTER_ZOOM)
            for idx in selected_pages:
                page = doc[idx]
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                b64 = base64.b64encode(img_bytes).decode("ascii")
                images_b64.append(b64)
                image_pages_1based.append(idx + 1)

        finally:
            doc.close()

        text_full = self._truncate(pages_data)
        return text_full, images_b64, image_pages_1based


# ===================================================================
# 5. multimodal_toc(V7 — TOC-based 精準頁定位 + multimodal 截圖)
# ===================================================================
# TOC 章節標題匹配的關鍵字（命中即視為「機械尺寸章節」）
_TOC_KEYWORDS = [
    "package outline", "package dimensions", "mechanical drawing",
    "mechanical dimensions", "body dimensions", "outline drawing",
    "footprint", "land pattern", "solder pad",
    # 單字 fallback
    "package", "mechanical", "outline", "dimensions",
]


class MultiModalTocExtractor(MultiModalExtractor):
    """V7：用 PyMuPDF doc.get_toc() 拿 PDF 目錄結構精準定位機械頁。

    流程：
    1. doc.get_toc() 拿目錄
    2. 找含 TOC 關鍵字的章節（命中越精確的章節越好）
    3. 取該章節起始頁 + 鄰頁
    4. 沒有 TOC / 沒命中 → fallback 到 MultiModalExtractor 關鍵字 grep
    """
    name = "multimodal_toc"

    def _extract_text_and_images(
        self, pdf_path: Path
    ) -> Tuple[str, List[str], List[int]]:
        import fitz

        pages_data: List[Dict] = []
        toc_target_pages: List[int] = []  # 0-based

        doc = fitz.open(str(pdf_path))
        try:
            # ---- 1. TOC 解析 ----
            toc = doc.get_toc()  # [[level, title, page_1based], ...]
            for entry in toc:
                if len(entry) < 3:
                    continue
                _, title, page = entry[0], entry[1], entry[2]
                if not isinstance(title, str):
                    continue
                title_lower = title.lower()
                if any(kw in title_lower for kw in _TOC_KEYWORDS):
                    # PyMuPDF TOC page 是 1-based
                    page_idx_0 = max(0, page - 1)
                    if page_idx_0 < config.MAX_PDF_PAGES:
                        toc_target_pages.append(page_idx_0)

            # ---- 2. 抽純文字（給 critic 用）----
            for idx, page in enumerate(doc):
                if idx >= config.MAX_PDF_PAGES:
                    break
                text = page.get_text() or ""
                table_chunks = []
                try:
                    tabs = page.find_tables()
                    for t in tabs.tables:
                        rows = t.extract()
                        row_strs = []
                        for row in rows:
                            cells = [str(c).strip() if c is not None else "" for c in row]
                            row_strs.append(" | ".join(cells))
                        if row_strs:
                            table_chunks.append("\n".join(row_strs))
                except Exception:
                    pass
                tbl_text = "\n\n".join(table_chunks)
                pages_data.append({
                    "page_num": idx + 1,
                    "text": text,
                    "tables": tbl_text,
                    "has_keyword": self._has_keyword(text, tbl_text),
                })

            # ---- 3. 決定候選頁：TOC 命中 → 用 TOC；否則 fallback 關鍵字 grep ----
            if toc_target_pages:
                # TOC 命中
                candidate_image_pages = toc_target_pages
            else:
                # Fallback: V4 關鍵字 grep
                candidate_image_pages = []
                for pd in pages_data:
                    lower = (pd["text"] + " " + pd["tables"]).lower()
                    if any(kw in lower for kw in _MULTIMODAL_KEYWORDS):
                        candidate_image_pages.append(pd["page_num"] - 1)

            # ---- 4. 擴展鄰頁 ----
            expanded = set()
            for p in candidate_image_pages:
                expanded.add(p)
                if p > 0:
                    expanded.add(p - 1)
                if p < doc.page_count - 1 and p + 1 < config.MAX_PDF_PAGES:
                    expanded.add(p + 1)
            selected_pages = sorted(expanded)[:_MAX_IMAGES]

            # ---- 5. 光柵化選中頁 ----
            images_b64: List[str] = []
            image_pages_1based: List[int] = []
            mat = fitz.Matrix(_RASTER_ZOOM, _RASTER_ZOOM)
            for idx in selected_pages:
                page = doc[idx]
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                b64 = base64.b64encode(img_bytes).decode("ascii")
                images_b64.append(b64)
                image_pages_1based.append(idx + 1)

        finally:
            doc.close()

        text_full = self._truncate(pages_data)
        return text_full, images_b64, image_pages_1based


# ===================================================================
# Factory
# ===================================================================
def get_pdf_extractor(name: Optional[str] = None) -> PdfExtractor:
    name = (name or os.environ.get("PDF_EXTRACTOR", "pdfplumber")).lower()
    if name == "pdfplumber":
        return PdfPlumberExtractor()
    elif name == "fitz" or name == "pymupdf":
        return FitzExtractor()
    elif name == "camelot":
        return CamelotExtractor()
    elif name == "multimodal":
        return MultiModalExtractor()
    elif name == "multimodal_toc":
        return MultiModalTocExtractor()
    else:
        raise ValueError(
            f"Unknown PDF_EXTRACTOR: {name!r}. "
            f"Valid: pdfplumber / fitz / camelot / multimodal / multimodal_toc"
        )
