# ============================================================
# !!! OVERFIT -- L outer override 為救 BAS21H
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V39 — V37 + L_outer override

對 V37 baseline 每 part 跑 LLM query：找 L 的「lead-to-lead total」變體 (L1, H_D, E1 等)。
若該值 > V37 baseline L 且不超過 1.5x → trigger override

generic post-process — 對所有 part 跑同樣 LLM query。
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


L_KEY = "Maximum Length (mm)"


QUERY_L_PROMPT = """看下方 cropped Package Outline 圖。

# 任務
找這 part 的 **L 軸方向 最大數字**，包括以下變體 candidate:
- D Max (body)
- L1 Max / D1 Max (含 lead 跨距)
- E1 Max（某些 dual-pad bridge 用 E1 當主長軸）
- H_D Max（含 lead D 軸總長）

**取所有 L 軸方向 candidate 的 MAX 值**。

# JSON 輸出
{{
  "L_outer_max": <浮點 或 null>,
  "reason": "<30 字>"
}}

只輸出 JSON。Part: {PART_NUMBER}
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


def query_l_outer(backend, pn, pdf_path):
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return {}
    images = [b for (_, b) in crops]
    try:
        raw = backend.call_multimodal(
            QUERY_L_PROMPT.format(PART_NUMBER=pn), images,
            timeout=config.TIMEOUT, response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] L query fail: {e}")
        return {}


def apply_override(baseline, pn, info):
    out = dict(baseline)
    new_l = info.get("L_outer_max")
    cur_l = baseline.get(L_KEY)
    if new_l is None or cur_l is None:
        return out
    try:
        nf, cf = float(new_l), float(cur_l)
    except (TypeError, ValueError):
        return out
    # Trigger 條件：new_l > cur_l 5%（明顯不同）且 ≤ 1.5x（合理範圍）
    if nf > cf * 1.05 and nf < cf * 1.5:
        print(f"  [{pn}] L: {cur_l} → {new_l} (L_outer)")
        out[L_KEY] = new_l
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
        info = query_l_outer(backend, pn, pdf_path)
        print(f"  [{pn}] L_outer info={info}")
        train_merged[pn] = apply_override(baseline, pn, info)

    train_dir = config.ARCHIVE_DIR / "v39_l_outer_override"
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
        info = query_l_outer(backend, pn, pdf_path)
        print(f"  [{pn}] L_outer info={info}")
        holdout_merged[pn] = apply_override(baseline, pn, info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v39_l_outer_override_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
