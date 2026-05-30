# ============================================================
# !!! OVERFIT -- 建在 V31，Llama critic
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V36 — V31 baseline + Llama-4-Maverick second-opinion critic

Llama vision arch ≠ GPT-4o (V31 主要靠 GPT-4o)，可能對某些 GPT-4o blind spot 有 different perspective。

對每 part 1 LLM call: 用 Llama 看圖 + V31 answer，問每欄是否需修正。
"""
import json
import os
import sys
import time
from pathlib import Path

# 注意：強制 Llama backend
os.environ["BACKEND"] = "azure_llama"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

import config
from llm_backend import get_backend
from pdf_extractor import MultiModalExtractor


CRITIC_PROMPT = """你是電子元件 datasheet 第二意見審查員（不同 vision model）。給你某個 LLM 已抽取的答案 + 原圖 + PDF text，請以**獨立視角**審視。

# Part Number
{PART_NUMBER}

# 已抽答案
{ANSWER}

# 重要 schema 規則
- L = D Max（JEDEC body D 軸）
- W = E Max（body E 軸）
- H = A Max（body A 軸）
- Min Op Temp = Tj range low；Tj 是 single max 而無 Tamb range 時用 Tj single
- I_O 優先於 I_F
- 必要時參考圖示判斷

# 任務
對下方欄位給 **更可能正確的值** 或標 null（表示同意 baseline）：

```json
{{
  "Maximum Length (mm)": <更可能值 或 null>,
  "Maximum Width (mm)": <值 或 null>,
  "Maximum Height (mm)": <值 或 null>,
  "Minimum Operating Temperature(°C)": <整數 或 null>,
  "Maximum Operating Temperature (°C)": <整數 或 null>,
  "PIN Number": <整數 或 null>,
  "I_O、I_F (A)": <浮點 或 null>,
  "V_F(Forward Voltage) (V)": <字串 或 null>,
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": <整數 或 null>,
  "I_R(Reverse Current) ": <字串 或 null>
}}
```

只輸出 JSON，前後不要文字。

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


def llama_critic(backend, pn, baseline, pdf_path):
    extractor = MultiModalExtractor()
    text, images, _ = extractor.extract_with_images(pdf_path)
    answer_json = json.dumps({k: v for k, v in baseline.items() if not k.startswith("_")}, ensure_ascii=False, indent=2)
    prompt = CRITIC_PROMPT.format(PART_NUMBER=pn, ANSWER=answer_json, TEXT=text[:6000])
    try:
        raw = backend.call_multimodal(
            prompt, images,
            timeout=config.TIMEOUT,
            response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] critic fail: {e}")
        return {}


def apply_critic(baseline, pn, suggestions):
    """Llama critic 的 suggestions: 若 value not null → 採 Llama 建議"""
    out = dict(baseline)
    for f in config.FIELDS:
        sug = suggestions.get(f)
        if sug is not None:
            cur = baseline.get(f)
            if str(cur) != str(sug):
                print(f"    [{pn}] {f}: {cur} → {sug} (Llama critic)")
                out[f] = sug
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train (Llama critic) ===")
    v31 = load_v31_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v31.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        print(f"  [{pn}] Llama critic...")
        sug = llama_critic(backend, pn, baseline, pdf_path)
        train_merged[pn] = apply_critic(baseline, pn, sug)

    train_dir = config.ARCHIVE_DIR / "v36_v31_with_llama_critic"
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
        print(f"  [{pn}] Llama critic...")
        sug = llama_critic(backend, pn, baseline, pdf_path)
        holdout_merged[pn] = apply_critic(baseline, pn, sug)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v36_v31_with_llama_critic_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
