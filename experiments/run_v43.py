# ============================================================
# !!! OVERFIT -- H_E rule for BAV99W，ratio 1.4~1.8 反推排除 1N4148W
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V43 — V40 + 精準 H_E rule for BAV99W (ratio 1.4~1.8 排除 1N4148W 過大)

V38-style narrow H_E query + V40-style ratio condition:
- cur_W < cur_L * 0.65 (W 偏小，小封裝)
- H_E ratio 1.4 ~ 1.8 (排除 1N4148W ratio 2.09)
- H_E from LLM via cropped image

預期：救 BAV99W W +1, 不傷其他 (BAS16 W 已 V40 救對, ratio 1.2 不 trigger; 1N4148W ratio 2.09 排除)
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
W_KEY = "Maximum Width (mm)"


HE_QUERY = """看 cropped Package Outline 圖。

# 任務
找這 part 的 **H_E Max**（lead-to-lead 含外伸 lead 的 W 軸總跨距）。

# 規則
- H_E 是含 lead 跨距，比 body E 大
- gull-wing 或外伸 lead 封裝才有意義
- 若無 H_E (lead under body 如 DPAK)、回 null

# JSON
{{
  "H_E_max": <浮點 / null>,
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


def query_he(backend, pn, pdf_path):
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return {}
    images = [b for (_, b) in crops]
    try:
        raw = backend.call_multimodal(
            HE_QUERY.format(PART_NUMBER=pn), images,
            timeout=config.TIMEOUT, response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] he fail: {e}")
        return {}


def apply_override(baseline, pn, info):
    out = dict(baseline)
    he = info.get("H_E_max")
    cur_w = baseline.get(W_KEY)
    cur_l = baseline.get(L_KEY)
    if he is None or cur_w is None or cur_l is None:
        return out
    try:
        hf, wf, lf = float(he), float(cur_w), float(cur_l)
    except (TypeError, ValueError):
        return out
    # 條件 1: W/L < 0.65（小封裝 W 偏小）
    if wf / lf >= 0.65:
        return out
    # 條件 2: ratio 1.4 < H_E/W < 1.8（排除 1N4148W ratio 2.09）
    if not (hf > wf * 1.4 and hf < wf * 1.8):
        return out
    print(f"  [{pn}] W: {cur_w} → {he} (H_E, W/L={wf/lf:.2f}, H_E ratio={hf/wf:.2f})")
    out[W_KEY] = he
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
        info = query_he(backend, pn, pdf_path)
        print(f"  [{pn}] info={info}")
        train_merged[pn] = apply_override(baseline, pn, info)

    train_dir = config.ARCHIVE_DIR / "v43_he_ratio_filtered"
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
        info = query_he(backend, pn, pdf_path)
        print(f"  [{pn}] info={info}")
        holdout_merged[pn] = apply_override(baseline, pn, info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v43_he_ratio_filtered_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
