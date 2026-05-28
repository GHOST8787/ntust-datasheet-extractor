"""比 V23 vs V12 cell diff，找出哪個 cell 從錯變對"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import json
import config
from evaluate_all import load_train_results, evaluate, find_actual_cell_id
from reevaluate import load_specbook
from main import cmp_numeric, cmp_text, cmp_exact

spec = load_specbook(config.SPECBOOK_PATH)
v12 = load_train_results(find_actual_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v23 = load_train_results(find_actual_cell_id("v23_majority_vote_3model"))

print("V12 → V23 cell diffs (only changed cells, with match status):\n")
for pn in spec.keys():
    a = v12.get(pn, {})
    b = v23.get(pn, {})
    exp_rec = spec[pn]
    for f in config.FIELDS:
        av = a.get(f)
        bv = b.get(f)
        if str(av) == str(bv):
            continue
        exp = exp_rec.get(f)
        if f in config.NUMERIC_FIELDS:
            a_ok = cmp_numeric(av, exp)
            b_ok = cmp_numeric(bv, exp)
        elif f in config.TEXT_FIELDS:
            a_ok = cmp_text(av, exp)[0]
            b_ok = cmp_text(bv, exp)[0]
        else:
            a_ok = cmp_exact(av, exp)
            b_ok = cmp_exact(bv, exp)
        change = ""
        if a_ok and not b_ok:
            change = " ✗ V12對→V23錯"
        elif not a_ok and b_ok:
            change = " ✓ V12錯→V23對"
        elif a_ok and b_ok:
            change = " (兩個都對)"
        else:
            change = " (兩個都錯)"
        print(f"  [{pn}] {f}")
        print(f"    V12 = {av!r}  (match={a_ok})")
        print(f"    V23 = {bv!r}  (match={b_ok})")
        print(f"    GT  = {exp!r}{change}")
        print()
