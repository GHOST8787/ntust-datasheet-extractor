"""V41 — V40 + Tj single + no-Tamb rule

對每 part LLM query: Tj 是 single value 嗎 + datasheet 有 Tamb range 嗎
- Tj single AND no Tamb → Min Op = Tj single value（救 BAV99W）
- Tj single AND has Tamb → 不 trigger（避免救錯 BAS16）

generic — 對所有 PDF 同樣判定流程
"""
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

import config
from llm_backend import get_backend
from pdf_extractor import MultiModalExtractor


TJ_QUERY = """看下方 datasheet 文字。判斷 Junction Temperature (Tj) 跟 Ambient Temperature (Tamb) 的標註結構。

# 規則
- Tj single: Tj 只一個 max 值（沒上下限 range）
- Tj range: Tj 有上下限（如 -55 to 150）
- has_tamb: datasheet 內 Maximum Ratings / Absolute Maximum Ratings 表是否有 **Tamb (Ambient Temperature)** 標籤跟 range

# JSON 輸出
{{
  "tj_is_single": true | false,
  "tj_single_value": <integer 若 single> or null,
  "has_tamb_range": true | false,
  "reason": "<50 字>"
}}

只輸出 JSON。Part: {PART_NUMBER}

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
        print(f"  [{pn}] tj query fail: {e}")
        return {}


def apply_override(baseline, pn, info):
    out = dict(baseline)
    if not info.get("tj_is_single"):
        return out
    if info.get("has_tamb_range"):
        return out  # 有 Tamb → 不 trigger
    val = info.get("tj_single_value")
    if val is None:
        return out
    cur = baseline.get("Minimum Operating Temperature(°C)")
    if str(cur) != str(val):
        print(f"  [{pn}] Min Op: {cur} → {val} (Tj single, no Tamb)")
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
        info = query_tj(backend, pn, pdf_path)
        print(f"  [{pn}] tj={info}")
        train_merged[pn] = apply_override(baseline, pn, info)

    train_dir = config.ARCHIVE_DIR / "v41_tj_single_no_tamb"
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
        info = query_tj(backend, pn, pdf_path)
        print(f"  [{pn}] tj={info}")
        holdout_merged[pn] = apply_override(baseline, pn, info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v41_tj_single_no_tamb_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
