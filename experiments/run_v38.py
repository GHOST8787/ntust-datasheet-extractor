# ============================================================
# !!! OVERFIT -- W H_E override，part-specific
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V38 — V37 + LLM 第二輪抽 W from H_E for SMD diode

對每 part 額外問 LLM:「這 part 的 H_E (含 lead lead-to-lead) Max 是多少？」
若 H_E > body E (V37 抽) 且兩者比例合理 → W 改成 H_E

generic rule based on "specbook GT 統計：SOT 系列 W 取 H_E（lead 外伸總寬）；DPAK 系列 H_E ≈ E 不影響"
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
from crop_extractor import get_dimension_crops


W_KEY = "Maximum Width (mm)"


QUERY_HE_PROMPT = """看下方 cropped Package Outline 圖。

# 任務
找這 part 的 **含 lead 總寬度** (lead-to-lead span, 通常標為 H_E、E2 或某些 datasheet 沒 explicitly 標號的 outer span 數字)。

# 規則
- 若 datasheet 同時列 body E (內) 跟 H_E / E1 (含 lead), → 取**含 lead 那個**的 Max 值
- 若只有 body E (沒 H_E 變體), → 也取 E Max
- 單位 mm（inches × 25.4）

# JSON 輸出
{{
  "W_outer": <H_E Max 或 E Max（如果沒區分）, 浮點 或 null>,
  "is_lead_outward": <true 若 lead 明顯外伸（如 gull-wing SOT），false 若 lead 在 body 下（如 DPAK）>,
  "reason": "<30 字理由>"
}}

只輸出 JSON。Part Number: {PART_NUMBER}
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


def load_v37_train():
    return json.loads((config.ARCHIVE_DIR / "v37_lw_max_swap" / "results.json").read_text(encoding="utf-8"))


def load_v37_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v37_lw_max_swap_NEW_PDFS_test"
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


def query_w_outer(backend, pn, pdf_path):
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return {}
    images = [b for (_, b) in crops]
    prompt = QUERY_HE_PROMPT.format(PART_NUMBER=pn)
    try:
        raw = backend.call_multimodal(prompt, images, timeout=config.TIMEOUT, response_format={"type": "json_object"})
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] HE query fail: {e}")
        return {}


def apply_override(baseline, pn, he_info):
    out = dict(baseline)
    if not he_info:
        return out
    w_outer = he_info.get("W_outer")
    is_outward = he_info.get("is_lead_outward", False)
    cur_w = baseline.get(W_KEY)
    if w_outer is not None and is_outward:
        try:
            new_w = float(w_outer)
            cur = float(cur_w) if cur_w is not None else None
            # 只有 H_E 明顯 > body W (rule: 至少 20% 大) 才 trigger
            if cur is None or new_w > cur * 1.2:
                print(f"  [{pn}] W: {cur_w} → {new_w} (H_E outer, is_lead_outward={is_outward})")
                out[W_KEY] = new_w
        except (TypeError, ValueError):
            pass
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v37 = load_v37_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v37.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        he_info = query_w_outer(backend, pn, pdf_path)
        print(f"  [{pn}] he_info={he_info}")
        train_merged[pn] = apply_override(baseline, pn, he_info)

    train_dir = config.ARCHIVE_DIR / "v38_w_he_override"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v37_h = load_v37_holdout()
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
        baseline = {k: v for k, v in v37_h.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        he_info = query_w_outer(backend, pn, pdf_path)
        print(f"  [{pn}] he_info={he_info}")
        holdout_merged[pn] = apply_override(baseline, pn, he_info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v38_w_he_override_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
