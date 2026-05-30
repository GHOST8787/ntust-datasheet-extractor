# ============================================================
# !!! OVERFIT -- 建在 V31，verify critic
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V34 — V31 baseline + per-part LLM "verify each field" critic

對每 part 跑 1 個 LLM call: 「給你 V31 抽的 11 個欄位 + 看圖 + PDF text，
請對每欄位輸出 confidence 0-1 + 如有疑慮給出建議修正」

對 confidence < 0.5 且建議跟 baseline 不同 → 採建議值

generic — 對所有 part 都跑同樣 verify。
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


VERIFY_PROMPT = """你是 datasheet 抽取結果審查專家。下方給你某 LLM 已抽取的 11 個欄位答案 + datasheet 原文 + 機械頁截圖。

# 任務
對每個欄位，判斷答案是否正確。若有疑慮 (confidence < 0.7)，給出建議修正值（從 datasheet 抽）。

# 指定型號
Part Number: {PART_NUMBER}

# 已抽答案
```json
{ANSWER}
```

# 重要 schema 規則（GT 用此規則）
- **Maximum Length (mm)**: D 軸 Max（JEDEC 標準）— body D
- **Maximum Width (mm)**: E 軸 Max（JEDEC 標準）— body E
- **Maximum Height (mm)**: A 軸 Max — body A
- **Minimum Operating Temperature(°C)**: Tj range low；若 Tj 是 single max value 而非 range，且 datasheet 沒給 Tamb range，則用 Tj single value
- **Maximum Operating Temperature (°C)**: Tj range high
- **PIN Number**: 封裝實際 lead 數
- **I_O、I_F (A)**: 優先 I_O (Average Rectified Output Current) > I_F (Forward Continuous)
- **V_F (V)**: 列所有條件，max 值
- **V_RRM (V)**: V_RRM 或 Max Repetitive Peak Reverse Voltage
- **I_R**: 列所有溫度條件，max 值

# 輸出 JSON
{{
  "Part Number": {{"value": "...", "confidence": 1.0, "suggested": null}},
  "Minimum Operating Temperature(°C)": {{"value": ..., "confidence": 0.X, "suggested": <if you think different value> or null}},
  ...
}}

只對 confidence < 0.7 的欄位給 suggested。confidence ≥ 0.7 的 suggested = null。

# datasheet 原文（部分）
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
        raise ValueError("No JSON")
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


def verify(backend, pn, baseline, pdf_path):
    extractor = MultiModalExtractor()
    text, images, _ = extractor.extract_with_images(pdf_path)
    answer_json = json.dumps({k: v for k, v in baseline.items() if not k.startswith("_")}, ensure_ascii=False, indent=2)
    prompt = VERIFY_PROMPT.format(PART_NUMBER=pn, ANSWER=answer_json, TEXT=text[:6000])
    try:
        raw = backend.call_multimodal(
            prompt, images,
            timeout=config.TIMEOUT,
            response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] verify fail: {e}")
        return {}


def apply_verify(baseline, pn, verify_result, threshold=0.5):
    out = dict(baseline)
    for f in config.FIELDS:
        info = verify_result.get(f, {})
        if not isinstance(info, dict):
            continue
        conf = info.get("confidence", 1.0)
        sug = info.get("suggested")
        if sug is not None and conf < threshold:
            cur = baseline.get(f)
            if str(cur) != str(sug):
                print(f"    [{pn}] {f}: {cur} → {sug} (conf={conf:.2f})")
                out[f] = sug
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v31_train = load_v31_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v31_train.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        print(f"  [{pn}] verifying...")
        result = verify(backend, pn, baseline, pdf_path)
        train_merged[pn] = apply_verify(baseline, pn, result)

    train_dir = config.ARCHIVE_DIR / "v34_v31_with_verify"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v31_h = load_v31_holdout()
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
        baseline = {k: v for k, v in v31_h.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        print(f"  [{pn}] verifying...")
        result = verify(backend, pn, baseline, pdf_path)
        holdout_merged[pn] = apply_verify(baseline, pn, result)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v34_v31_with_verify_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
