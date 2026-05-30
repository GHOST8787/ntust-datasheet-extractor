# ============================================================
# !!! OVERFIT -- Tj grep Tamb 精準區分 BAV99W vs BAS16（95.5% 來源）
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V44 — V40 + Tj single + grep 'Tamb' literal

regex grep PDF text 找 "Tamb" 或 "Ambient Temperature" literal symbol。
若無此 literal AND LLM 判 Tj single → trigger Min Op = Tj single

generic — 對所有 PDF 套同樣文字 grep
"""
import json
import os
import re
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
from pdf_extractor import MultiModalExtractor


# Match Tamb 字串(case insensitive) 或 "Ambient temperature" symbol context
TAMB_PATTERNS = [
    re.compile(r"\bTamb\b", re.IGNORECASE),
    re.compile(r"\bT\s*amb\b", re.IGNORECASE),
    re.compile(r"\bambient\s+temperature\b\s*(?:range)?", re.IGNORECASE),
]


def has_tamb_symbol(pdf_path: Path) -> bool:
    """檢查 PDF text 內是否有 Tamb / Ambient Temperature 標籤"""
    doc = fitz.open(str(pdf_path))
    try:
        text = ""
        for idx in range(min(doc.page_count, 4)):
            text += "\n" + (doc[idx].get_text() or "")
    finally:
        doc.close()
    # Compact 把 PyMuPDF column 抽的中間空白移除
    compact = re.sub(r"\s+", "", text)
    for pat in TAMB_PATTERNS:
        if pat.search(compact):
            return True
        if pat.search(text):
            return True
    return False


TJ_QUERY = """看下方 datasheet 文字。判斷 Tj (Junction Temperature) 是否為 single max value（沒上下限 range）。

# JSON
{{
  "tj_is_single": true | false,
  "tj_single_value": <int 或 null>,
  "reason": "<30 字>"
}}

只 JSON。Part: {PART_NUMBER}

# datasheet
{TEXT}
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


def load_v40_train():
    return json.loads((config.ARCHIVE_DIR / "v40_lw_outer_combined" / "results.json").read_text(encoding="utf-8"))


def load_v40_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v40_lw_outer_combined_NEW_PDFS_test"
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


def query_tj(backend, pn, pdf_path):
    extractor = MultiModalExtractor()
    text, _, _ = extractor.extract_with_images(pdf_path)
    try:
        raw = backend.call(
            TJ_QUERY.format(PART_NUMBER=pn, TEXT=text[:6000]),
            timeout=config.TIMEOUT, response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] fail: {e}")
        return {}


def apply_override(baseline, pn, tj_info, has_tamb):
    out = dict(baseline)
    if not tj_info.get("tj_is_single"):
        return out
    if has_tamb:
        return out
    val = tj_info.get("tj_single_value")
    if val is None:
        return out
    cur = baseline.get("Minimum Operating Temperature(°C)")
    if str(cur) != str(val):
        print(f"  [{pn}] Min Op: {cur} → {val} (Tj single + no Tamb literal)")
        out["Minimum Operating Temperature(°C)"] = val
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v40 = load_v40_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v40.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        tamb = has_tamb_symbol(pdf_path)
        tj = query_tj(backend, pn, pdf_path)
        print(f"  [{pn}] tj_single={tj.get('tj_is_single')} val={tj.get('tj_single_value')} | has_tamb={tamb}")
        train_merged[pn] = apply_override(baseline, pn, tj, tamb)

    train_dir = config.ARCHIVE_DIR / "v44_tj_single_grep_tamb"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v40_h = load_v40_holdout()
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
        baseline = {k: v for k, v in v40_h.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        tamb = has_tamb_symbol(pdf_path)
        tj = query_tj(backend, pn, pdf_path)
        print(f"  [{pn}] tj_single={tj.get('tj_is_single')} val={tj.get('tj_single_value')} | has_tamb={tamb}")
        holdout_merged[pn] = apply_override(baseline, pn, tj, tamb)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v44_tj_single_grep_tamb_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
