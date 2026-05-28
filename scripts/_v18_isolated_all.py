"""分析 V12/V18/V22 在 L/W/H 上所有 isolation pattern + 相對 ratio"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import json
import config
from evaluate_all import load_train_results, find_actual_cell_id
from reevaluate import load_specbook
from main import cmp_numeric

DIM = ["Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"]

spec = load_specbook(config.SPECBOOK_PATH)
v12 = load_train_results(find_actual_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v18 = load_train_results(find_actual_cell_id("v18_multimodal_azure_llama_4_maverick_conservative"))
v22 = load_train_results(find_actual_cell_id("v22_multimodal_toc_azure_gpt_4o_conservative"))

# 對每個 part 看 L/W/H 三軸的 isolation pattern + V18/V12 ratio
print(f"{'Part':<12} {'Axis':<8} {'V12':>8} {'V18':>8} {'V22':>8} {'GT':>8} {'V18/V12':>9} {'iso':>6}")
print("-" * 75)
for pn in spec.keys():
    a = v12.get(pn, {})
    b = v18.get(pn, {})
    c = v22.get(pn, {})
    exp_rec = spec[pn]
    for f, ax in zip(DIM, ["L", "W", "H"]):
        av, bv, cv = a.get(f), b.get(f), c.get(f)
        sa, sb, sc = str(av), str(bv), str(cv)
        iso = "—"
        if sa == sc and sa != sb:
            iso = "v18"
        elif sa == sb and sa != sc:
            iso = "v22"
        elif sb == sc and sb != sa:
            iso = "v12"
        elif sa == sb == sc:
            iso = "all3"
        else:
            iso = "all3≠"
        try:
            ratio = float(bv) / float(av) if float(av) != 0 else None
            ratio_str = f"{ratio:.3f}" if ratio else "—"
        except (TypeError, ValueError):
            ratio_str = "—"
        gt = exp_rec.get(f)
        # mark which is correct
        a_ok = cmp_numeric(av, gt)
        b_ok = cmp_numeric(bv, gt)
        marks = "".join([
            "✓" if a_ok else "✗",
            "✓" if b_ok else "✗",
        ])
        print(f"{pn:<12} {ax:<8} {str(av):>8} {str(bv):>8} {str(cv):>8} {str(gt):>8} {ratio_str:>9} {iso:>6}  v12={marks[0]} v18={marks[1]}")
