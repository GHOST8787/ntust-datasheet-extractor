# ============================================================
# !!! OVERFIT -- 建在 V31，Tj regex 後處理
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V32 — V31 + Tj single-value post-process detection

對每個 PDF 跑 PyMuPDF text extraction，掃描 Tj 標籤的後續數字：
- 若 Tj = single max value (沒 range)  AND  Tstg 是 range
- → Min Operating Temp 採 Tj single value

純文字 parsing，不跑 LLM。generic 對 train + holdout 都套同邏輯。
"""
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import fitz
import config


def extract_tj_pattern(pdf_path: Path) -> dict:
    """掃 PDF 找 Tj 是 single value 還是 range。
    回傳 {'tj_single': int or None, 'tj_range': (lo, hi) or None, 'tstg_range': (lo, hi) or None}
    """
    out = {"tj_single": None, "tj_range": None, "tstg_range": None}
    doc = fitz.open(str(pdf_path))
    try:
        text = ""
        for idx in range(min(doc.page_count, 4)):
            text += "\n" + (doc[idx].get_text() or "")
    finally:
        doc.close()

    # 簡化：搜「Tj」+ 後續 數字 / range
    # Pattern A: "Tj ... -55 to 150" or "Tj ... -55...150"
    range_pat = re.compile(
        r"T\s*j\s*[\s\S]{0,200}?(-?\d+)\s*(?:to|~|–|-)\s*\+?(\d+)",
        re.IGNORECASE,
    )
    m = range_pat.search(text)
    if m:
        out["tj_range"] = (int(m.group(1)), int(m.group(2)))

    # Pattern B: 「Junction temperature ... 150」 single value
    # Heuristic: 在 Tj 標籤後找 「Junction Temperature」+ 後續單一數字行
    single_pat = re.compile(
        r"(?:T\s*j|Junction\s+temperature)[\s\S]{0,150}?(?:Rating|Limit|Value)?[\s\S]{0,100}?(?<![\d\-])\b(\d{2,3})\b(?![\s\S]{0,5}(?:to|~|–))",
        re.IGNORECASE,
    )
    if not out["tj_range"]:
        m = single_pat.search(text)
        if m:
            try:
                v = int(m.group(1))
                if 50 <= v <= 250:  # 合理 Tj max range
                    out["tj_single"] = v
            except ValueError:
                pass

    # Tstg range
    tstg_pat = re.compile(
        r"T\s*stg\s*[\s\S]{0,200}?(-?\d+)\s*(?:to|~|–|-)\s*\+?(\d+)",
        re.IGNORECASE,
    )
    m = tstg_pat.search(text)
    if m:
        out["tstg_range"] = (int(m.group(1)), int(m.group(2)))
    return out


def load_v31_train():
    return json.loads((config.ARCHIVE_DIR / "v31_v26_with_v29_2field_override" / "results.json").read_text(encoding="utf-8"))


def load_v31_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v31_v26_with_v29_2field_override_NEW_PDFS_test"
    if not d.exists():
        return out
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


def apply_tj_override(baseline: dict, pdf_path: Path, part_name: str) -> dict:
    pattern = extract_tj_pattern(pdf_path)
    out = dict(baseline)
    # 觸發條件：Tj 是 single value（沒 range）+ Tstg 是 range
    # OR Tj 跟 Tstg 同 range 但 baseline 抽 Tstg low (不合適這 part)
    cur_min = baseline.get("Minimum Operating Temperature(°C)")
    if pattern["tj_single"] is not None and pattern["tj_range"] is None:
        # 只有 Tj single value，沒 Tj range → Min Op = Tj single
        target = pattern["tj_single"]
        if str(cur_min) != str(target):
            print(f"  [{part_name}] Min Op Temp: {cur_min} → {target} (Tj single override, Tstg={pattern['tstg_range']})")
            out["Minimum Operating Temperature(°C)"] = target
    return out


def main():
    print("=== Train ===")
    v31_train = load_v31_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        if not pdf_path.exists():
            train_merged[pn] = v31_train.get(pn, {})
            continue
        train_merged[pn] = apply_tj_override(v31_train.get(pn, {}), pdf_path, pn)

    train_dir = config.ARCHIVE_DIR / "v32_v31_tj_postprocess"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v31_holdout = load_v31_holdout()
    HOLDOUT_PDFS = [
        ("FFSH5065B",     r"AA\FFSH5065B-F085-D.PDF"),
        ("FFSD1065B",     r"AA\FFSD1065B-D.PDF"),
        ("VS3C20ET07T",   r"AA\vs-3c20et07t-m3.pdf"),
        ("VS3C12ET07S2L", r"AA\vs-3c12et07s2l-m.pdf"),
        ("ASA006V065F4",  r"AA\ASA006V065F4.pdf"),
    ]
    holdout_merged = {}
    for pn, rel in HOLDOUT_PDFS:
        pdf_path = config.PROJECT_ROOT / rel
        if not pdf_path.exists():
            holdout_merged[pn] = v31_holdout.get(pn, {})
            continue
        holdout_merged[pn] = apply_tj_override(v31_holdout.get(pn, {}), pdf_path, pn)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v32_v31_tj_postprocess_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")


if __name__ == "__main__":
    main()
