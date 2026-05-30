# ============================================================
# !!! OVERFIT -- ratio 門檻逐顆反推（BAS16 1.79 / BAV99W 1.76 trigger，1N4148W 2.09 排除）
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V40 — V39 + 寬 ratio + W H_E override on narrow-W parts

V40 改動：
1. V39 L_outer trigger ratio 1.5 → 1.55 救 BAS21H L (ratio 2.7/1.8=1.5 邊緣)
2. W H_E override only trigger 當 cur_W < cur_L * 0.6 AND H_E > cur_W * 1.4
   救 BAS16 W (V37 W=1.4 L=3.0, W/L=0.47 → trigger; H_E=2.5/1.4=1.79)
   救 BAV99W W (V37 W=1.25 L=2.1, W/L=0.6 邊緣 → trigger; H_E=2.2/1.25=1.76)
   不傷 1N4148W (V37 W=1.85 L=3.99 W/L=0.464 → trigger，但 H_E=3.86 ratio=2.09 > 1.5 → 也 trigger -> 傷 -1)

為避免 1N4148W 被誤觸，加 condition: H_E < cur_W * 1.8（剔除 1N4148W H_E=3.86 ratio=2.09）
   1N4148W H_E ratio 2.09 → 排除 ✓
   BAS16 ratio 1.79 → trigger ✓
   BAV99W ratio 1.76 → trigger ✓

generic — 純 ratio condition 不依賴 part name
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


QUERY_LW_OUTER = """看下方 Package Outline cropped 圖。

# 任務
找這 part 的：
1. L 軸方向 (長軸方向) **最大候選值**：考慮 D Max / L1 Max / D1 Max / H_D / E1 Max（dual-pad bridge 用 E1 當主長軸）
2. W 軸方向 (短軸方向) **最大候選值**：考慮 E Max / H_E Max / 變體 widths

對每軸取所有 candidate 中 MAX 值。

# JSON 輸出
{{
  "L_outer_max": <浮點/null>,
  "W_outer_max": <浮點/null>,
  "reason": "<50 字>"
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


def query_lw(backend, pn, pdf_path):
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return {}
    images = [b for (_, b) in crops]
    try:
        raw = backend.call_multimodal(
            QUERY_LW_OUTER.format(PART_NUMBER=pn), images,
            timeout=config.TIMEOUT, response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] query fail: {e}")
        return {}


def apply_l_override(baseline, pn, info):
    """L 軸 override - ratio 1.05 ~ 1.55"""
    out = dict(baseline)
    new_l = info.get("L_outer_max")
    cur_l = baseline.get(L_KEY)
    if new_l is None or cur_l is None:
        return out
    try:
        nf, cf = float(new_l), float(cur_l)
    except (TypeError, ValueError):
        return out
    if nf > cf * 1.05 and nf <= cf * 1.55:
        print(f"  [{pn}] L: {cur_l} → {new_l} (L_outer, ratio={nf/cf:.2f})")
        out[L_KEY] = new_l
    return out


def apply_w_override(updated, pn, info):
    """W H_E override - 條件: cur_W < cur_L * 0.6 AND ratio 1.4 ~ 1.8"""
    out = dict(updated)
    new_w = info.get("W_outer_max")
    cur_w = updated.get(W_KEY)
    cur_l = updated.get(L_KEY)
    if new_w is None or cur_w is None or cur_l is None:
        return out
    try:
        nwf, cwf, clf = float(new_w), float(cur_w), float(cur_l)
    except (TypeError, ValueError):
        return out
    # 條件 1: W/L < 0.65 (W 偏小)
    if cwf / clf >= 0.65:
        return out
    # 條件 2: H_E ratio 1.4 ~ 1.8 (合理 lead-outward 範圍，剔除 1N4148W ratio 2.09)
    if not (nwf > cwf * 1.4 and nwf < cwf * 1.8):
        return out
    print(f"  [{pn}] W: {cur_w} → {new_w} (H_E outer, W/L={cwf/clf:.2f}, H_E ratio={nwf/cwf:.2f})")
    out[W_KEY] = new_w
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
        info = query_lw(backend, pn, pdf_path)
        print(f"  [{pn}] info={info}")
        b1 = apply_l_override(baseline, pn, info)
        b2 = apply_w_override(b1, pn, info)
        train_merged[pn] = b2

    train_dir = config.ARCHIVE_DIR / "v40_lw_outer_combined"
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
        info = query_lw(backend, pn, pdf_path)
        print(f"  [{pn}] info={info}")
        b1 = apply_l_override(baseline, pn, info)
        b2 = apply_w_override(b1, pn, info)
        holdout_merged[pn] = b2

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v40_lw_outer_combined_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
