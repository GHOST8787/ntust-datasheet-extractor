"""V29 vs V12 全 cell diff，分 train + holdout"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import json
import config
from evaluate_all import load_train_results, load_holdout_results, find_actual_cell_id, find_actual_holdout_cell_id
from reevaluate import load_specbook
from evaluate_new_5 import GROUND_TRUTH as HOLDOUT_GT
from main import cmp_numeric, cmp_text, cmp_exact


def is_correct(val, exp, field):
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(val, exp)
    elif field in config.TEXT_FIELDS:
        return cmp_text(val, exp)[0]
    return cmp_exact(val, exp)


spec = load_specbook(config.SPECBOOK_PATH)
v12 = load_train_results(find_actual_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v29 = load_train_results(find_actual_cell_id("v29_multimodal_azure_gpt_4o_conservative"))

print("=== TRAIN diffs (V12 → V29) ===")
for pn in spec.keys():
    a, b = v12.get(pn, {}), v29.get(pn, {})
    exp_rec = spec[pn]
    for f in config.FIELDS:
        if str(a.get(f)) != str(b.get(f)):
            a_ok = is_correct(a.get(f), exp_rec.get(f), f)
            b_ok = is_correct(b.get(f), exp_rec.get(f), f)
            mark = "✓對→錯" if a_ok and not b_ok else ("✗錯→對" if not a_ok and b_ok else ("=都對" if a_ok else "=都錯"))
            print(f"  {pn:<14} {f:<42} V12={str(a.get(f))[:25]:<25} → V29={str(b.get(f))[:25]:<25} GT={str(exp_rec.get(f))[:15]:<15} {mark}")

print()
print("=== HOLDOUT diffs (V12 → V29) ===")
v12_h = load_holdout_results(find_actual_holdout_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v29_h = load_holdout_results(find_actual_holdout_cell_id("v29_multimodal_azure_gpt_4o_conservative"))
for pn, exp_rec in HOLDOUT_GT.items():
    a, b = v12_h.get(pn, {}), v29_h.get(pn, {})
    for f in config.FIELDS:
        if str(a.get(f)) != str(b.get(f)):
            a_ok = is_correct(a.get(f), exp_rec.get(f), f)
            b_ok = is_correct(b.get(f), exp_rec.get(f), f)
            mark = "✓對→錯" if a_ok and not b_ok else ("✗錯→對" if not a_ok and b_ok else ("=都對" if a_ok else "=都錯"))
            print(f"  {pn:<14} {f:<42} V12={str(a.get(f))[:25]:<25} → V29={str(b.get(f))[:25]:<25} GT={str(exp_rec.get(f))[:15]:<15} {mark}")
