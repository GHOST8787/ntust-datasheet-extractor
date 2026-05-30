# ============================================================
# !!! OVERFIT -- 建在 V31，Tj LLM query 後處理
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V33 — V31 + LLM Tj structure query post-process

對每 part 跑 1 LLM call，問 datasheet 的 Tj 是 single value 還是 range。
- 若 single value (例 Tj = 150°C max) → Min Op Temp = Tj single
- 若 range → 維持 V31 baseline

純 generic 一輪 LLM 確認。
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


TJ_QUERY_PROMPT = """看下方 datasheet 文字 + 圖（如有），找 Junction Temperature (Tj) 的 rating 是 single value 還是 range。

# 任務
分析 datasheet 內 Tj 標籤的 rating 欄位（不是 Tstg）。

# 規則
- "single": Tj 只有一個 max 值（例 `Tj = 150°C max`，沒給 min/lo bound）
- "range": Tj 是上下限 range（例 `Tj = -55 to 150°C`）

# 輸出 JSON
{{
  "tj_type": "single" | "range",
  "tj_value": <single max 值（整數）> 若 single，否則 null,
  "tj_lo": <range 下限> 若 range，否則 null,
  "tj_hi": <range 上限> 若 range，否則 null,
  "reason": "<簡短理由 30 字>"
}}

只輸出 JSON，前後不要文字。

# datasheet text
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
        raise ValueError(f"No JSON")
    return json.loads(text[s:e + 1])


def load_v31_train():
    return json.loads((config.ARCHIVE_DIR / "v31_v26_with_v29_2field_override" / "results.json").read_text(encoding="utf-8"))


def load_v31_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v31_v26_with_v29_2field_override_NEW_PDFS_test"
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


def query_tj(backend, pdf_path: Path):
    extractor = MultiModalExtractor()
    text, _, _ = extractor.extract_with_images(pdf_path)
    # 限文字 6K 避免 token 浪費
    prompt = TJ_QUERY_PROMPT.format(TEXT=text[:6000])
    try:
        raw = backend.call(prompt, timeout=config.TIMEOUT, response_format={"type": "json_object"})
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  Tj query fail: {e}")
        return {}


def apply_override(baseline, pn, tj_info):
    out = dict(baseline)
    cur_min = baseline.get("Minimum Operating Temperature(°C)")
    if tj_info.get("tj_type") == "single" and tj_info.get("tj_value") is not None:
        target = int(tj_info["tj_value"])
        if str(cur_min) != str(target):
            print(f"  [{pn}] Min Op Temp: {cur_min} → {target} (Tj single, reason={tj_info.get('reason', '')[:60]})")
            out["Minimum Operating Temperature(°C)"] = target
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v31_train = load_v31_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = v31_train.get(pn, {})
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        tj_info = query_tj(backend, pdf_path)
        print(f"  [{pn}] tj_info={tj_info}")
        train_merged[pn] = apply_override(baseline, pn, tj_info)

    train_dir = config.ARCHIVE_DIR / "v33_v31_tj_llm_query"
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
        baseline = v31_holdout.get(pn, {})
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        tj_info = query_tj(backend, pdf_path)
        print(f"  [{pn}] tj_info={tj_info}")
        holdout_merged[pn] = apply_override(baseline, pn, tj_info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v33_v31_tj_llm_query_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")

    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
