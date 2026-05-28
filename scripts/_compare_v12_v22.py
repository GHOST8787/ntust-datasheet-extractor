"""快速比 V12 vs V22 per-field errors"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import json
import config
from evaluate_all import load_train_results, load_holdout_results, evaluate, find_actual_cell_id, find_actual_holdout_cell_id
from reevaluate import load_specbook
from evaluate_new_5 import GROUND_TRUTH as HOLDOUT_GT

VERSIONS = [
    ("V12", "v12_multimodal_azure_gpt_4o_conservative"),
    ("V22", "v22_multimodal_toc_azure_gpt_4o_conservative"),
]

spec = load_specbook(config.SPECBOOK_PATH)
for label, base in VERSIONS:
    cell = find_actual_cell_id(base)
    t_data = load_train_results(cell)
    if not t_data:
        print(f"{label}: missing")
        continue
    t = evaluate(t_data, spec, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD)
    print(f"{label} train: {t['correct']}/{t['total']} = {t['accuracy']*100:.1f}%")

    # holdout
    h_cell = find_actual_holdout_cell_id(base)
    h_data = load_holdout_results(h_cell)
    if h_data:
        h = evaluate(h_data, HOLDOUT_GT, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD)
        print(f"{label} holdout: {h['correct']}/{h['total']} = {h['accuracy']*100:.1f}%")

# per-cell diff
print()
print("V12 vs V22 cell diffs (train):")
v12 = load_train_results(find_actual_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v22 = load_train_results(find_actual_cell_id("v22_multimodal_toc_azure_gpt_4o_conservative"))
for pn in spec.keys():
    a = v12.get(pn, {})
    b = v22.get(pn, {})
    for f in config.FIELDS:
        if str(a.get(f)) != str(b.get(f)):
            print(f"  {pn:<15} {f:<42} V12={a.get(f)!r:<30} V22={b.get(f)!r}")
