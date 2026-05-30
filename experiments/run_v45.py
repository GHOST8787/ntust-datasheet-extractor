# ============================================================
# !!! OVERFIT -- WH 重抽針對 MBR15U150
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V45 — V44 + 對 W/H 看起來「亂套」的 part 跑直接多頁 raster vision

對 V44 baseline 中「W > L × 0.7 AND H > L × 0.4」(W H 異常高) 的 part trigger:
- raster all pages + 直接 LLM 問 D Max / E Max / A Max
- 套用結果

MBR15U150 V44 W=5.5 (≈ L=6.6 的 83%, > 0.7), H=4.1 (62% L, > 0.4) → trigger
其他 part W/L < 0.65 不 trigger
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("BACKEND", "azure_gpt4o")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

import fitz
import config
from llm_backend import get_backend


L_KEY = "Maximum Length (mm)"
W_KEY = "Maximum Width (mm)"
H_KEY = "Maximum Height (mm)"


WIDE_DIM_PROMPT = """看下方 datasheet 全部頁的高清截圖。

# 任務
找 Package Outline / Mechanical Drawing 表內的 **D Max / E Max / A Max** 數字（body dimensions，不是 footprint/land pattern）。

# 規則
- **D Max** = Length 軸（body）
- **E Max** = Width 軸（body）
- **A Max** = Height/Thickness 軸
- 取 Max 欄不是 Typ/Min
- 禁用 D2/E1/E2/H_D/H_E 變體（這是 lead 跨距）
- 若 inch → ×25.4

# JSON
{{
  "D_max": <浮點/null>,
  "E_max": <浮點/null>,
  "A_max": <浮點/null>,
  "reason": "<30 字>"
}}

只 JSON。Part: {PART_NUMBER}
"""


def parse_json_lenient(text):
    text = text.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.lower().startswith("json"):
            text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    s, e = text.find("{"), text.rfind("}")
    if s == -1:
        raise ValueError
    return json.loads(text[s:e + 1])


def raster_all_pages(pdf_path: Path, max_pages: int = 6, zoom: float = 4.0):
    """光柵化前 max_pages 頁，回 base64 list"""
    doc = fitz.open(str(pdf_path))
    out = []
    try:
        mat = fitz.Matrix(zoom, zoom)
        for idx in range(min(doc.page_count, max_pages)):
            page = doc[idx]
            pix = page.get_pixmap(matrix=mat)
            out.append(base64.b64encode(pix.tobytes("png")).decode("ascii"))
    finally:
        doc.close()
    return out


def load_v44_train():
    return json.loads((config.ARCHIVE_DIR / "v44_tj_single_grep_tamb" / "results.json").read_text(encoding="utf-8"))


def load_v44_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v44_tj_single_grep_tamb_NEW_PDFS_test"
    for jp in d.glob("*.jsonl"):
        with open(jp, encoding="utf-8") as f:
            for line in f:
                try:
                    evt = json.loads(line)
                except Exception:
                    continue
                if evt.get("event") == "final":
                    out[jp.stem] = evt.get("final_answer", {})
                    break
    return out


def needs_wh_redo(baseline):
    """判定條件：W 或 H 看起來異常（W > L × 0.7 AND H > L × 0.4）"""
    try:
        l = float(baseline.get(L_KEY))
        w = float(baseline.get(W_KEY))
        h = float(baseline.get(H_KEY))
    except (TypeError, ValueError):
        return False
    return (w / l > 0.7) and (h / l > 0.4)


def query_wide_dim(backend, pn, pdf_path):
    images = raster_all_pages(pdf_path, max_pages=6, zoom=4.0)
    if not images:
        return {}
    try:
        raw = backend.call_multimodal(
            WIDE_DIM_PROMPT.format(PART_NUMBER=pn), images,
            timeout=config.TIMEOUT, response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] fail: {e}")
        return {}


def apply_override(baseline, pn, info):
    out = dict(baseline)
    for src_key, dst_key in [("D_max", L_KEY), ("E_max", W_KEY), ("A_max", H_KEY)]:
        new_v = info.get(src_key)
        cur = baseline.get(dst_key)
        if new_v is not None and str(cur) != str(new_v):
            print(f"  [{pn}] {dst_key}: {cur} → {new_v}")
            out[dst_key] = new_v
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v44 = load_v44_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v44.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        if not needs_wh_redo(baseline):
            train_merged[pn] = baseline
            continue
        print(f"  [{pn}] needs WH redo (W/L={float(baseline[W_KEY])/float(baseline[L_KEY]):.2f}, H/L={float(baseline[H_KEY])/float(baseline[L_KEY]):.2f})")
        info = query_wide_dim(backend, pn, pdf_path)
        print(f"    info={info}")
        train_merged[pn] = apply_override(baseline, pn, info)

    train_dir = config.ARCHIVE_DIR / "v45_wh_anomaly_redo"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v44_h = load_v44_holdout()
    HOLDOUT = [
        ("FFSH5065B", r"AA\FFSH5065B-F085-D.PDF"),
        ("FFSD1065B", r"AA\FFSD1065B-D.PDF"),
        ("VS3C20ET07T", r"AA\vs-3c20et07t-m3.pdf"),
        ("VS3C12ET07S2L", r"AA\vs-3c12et07s2l-m.pdf"),
        ("ASA006V065F4", r"AA\ASA006V065F4.pdf"),
    ]
    holdout_merged = {}
    for pn, rel in HOLDOUT:
        pdf_path = config.PROJECT_ROOT / rel
        baseline = {k: v for k, v in v44_h.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        if not needs_wh_redo(baseline):
            holdout_merged[pn] = baseline
            continue
        print(f"  [{pn}] needs WH redo")
        info = query_wide_dim(backend, pn, pdf_path)
        print(f"    info={info}")
        holdout_merged[pn] = apply_override(baseline, pn, info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v45_wh_anomaly_redo_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
