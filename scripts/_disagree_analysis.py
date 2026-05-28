"""分析 V12/V18/V22 三模型在 train errors 上的 disagreement pattern"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import json
import config
from evaluate_all import load_train_results, find_actual_cell_id
from reevaluate import load_specbook
from main import cmp_numeric, cmp_text, cmp_exact

spec = load_specbook(config.SPECBOOK_PATH)
v12 = load_train_results(find_actual_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v18 = load_train_results(find_actual_cell_id("v18_multimodal_azure_llama_4_maverick_conservative"))
v22 = load_train_results(find_actual_cell_id("v22_multimodal_toc_azure_gpt_4o_conservative"))
v23 = load_train_results(find_actual_cell_id("v23_majority_vote_3model"))


def is_correct(val, exp, field):
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(val, exp)
    elif field in config.TEXT_FIELDS:
        ok, _ = cmp_text(val, exp)
        return ok
    return cmp_exact(val, exp)


# 對 V23 仍錯的 cells 分析三模型 vote 分佈
errors_by_pattern = {
    "all3_same_wrong": [],         # 三個都同樣抽錯 (LLM 系統性錯)
    "v18_correct": [],             # V18 對但被多數 outvote
    "v22_correct": [],             # V22 對但被多數 outvote
    "v12_correct_outvoted": [],    # V12 對但被 outvote
    "all3_different": [],          # 三個都不同 — 真難
    "other": [],
}

for pn, exp_rec in spec.items():
    a = v12.get(pn, {})
    b = v18.get(pn, {})
    c = v22.get(pn, {})
    final = v23.get(pn, {})
    for f in config.FIELDS:
        if is_correct(final.get(f), exp_rec.get(f), f):
            continue
        # V23 在這 cell 錯了
        av, bv, cv = a.get(f), b.get(f), c.get(f)
        a_ok = is_correct(av, exp_rec.get(f), f)
        b_ok = is_correct(bv, exp_rec.get(f), f)
        c_ok = is_correct(cv, exp_rec.get(f), f)
        sa, sb, sc = str(av), str(bv), str(cv)

        info = {
            "part": pn, "field": f,
            "v12": av, "v18": bv, "v22": cv, "gt": exp_rec.get(f),
            "v12_ok": a_ok, "v18_ok": b_ok, "v22_ok": c_ok,
        }
        if a_ok or b_ok or c_ok:
            # 有人抽對了！
            if a_ok:
                errors_by_pattern["v12_correct_outvoted"].append(info)
            elif b_ok:
                errors_by_pattern["v18_correct"].append(info)
            else:
                errors_by_pattern["v22_correct"].append(info)
        elif sa == sb == sc:
            errors_by_pattern["all3_same_wrong"].append(info)
        elif sa != sb and sb != sc and sa != sc:
            errors_by_pattern["all3_different"].append(info)
        else:
            errors_by_pattern["other"].append(info)

print("V23 仍錯 cells 分析（按三模型 vote pattern 分類）:")
for k, lst in errors_by_pattern.items():
    print(f"\n=== {k} ({len(lst)}) ===")
    for info in lst:
        print(f"  [{info['part']}] {info['field']}")
        print(f"    GT  = {info['gt']!r}")
        print(f"    V12 = {info['v12']!r} {'✓' if info['v12_ok'] else '✗'}")
        print(f"    V18 = {info['v18']!r} {'✓' if info['v18_ok'] else '✗'}")
        print(f"    V22 = {info['v22']!r} {'✓' if info['v22_ok'] else '✗'}")
