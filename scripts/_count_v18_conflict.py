"""算 V12 == V22 ≠ V18 的 cells 數量（V18 是少數派）"""
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

spec = load_specbook(config.SPECBOOK_PATH)

# train
v12 = load_train_results(find_actual_cell_id("v12_multimodal_azure_gpt_4o_conservative"))
v18 = load_train_results(find_actual_cell_id("v18_multimodal_azure_llama_4_maverick_conservative"))
v22 = load_train_results(find_actual_cell_id("v22_multimodal_toc_azure_gpt_4o_conservative"))


def is_correct(val, exp, field):
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(val, exp)
    elif field in config.TEXT_FIELDS:
        ok, _ = cmp_text(val, exp)
        return ok
    return cmp_exact(val, exp)


def count_conflicts(v12_d, v18_d, v22_d, gt_dict):
    out = {"v18_isolated": [], "gpt4o_isolated": []}
    for pn, exp_rec in gt_dict.items():
        a = v12_d.get(pn, {})
        b = v18_d.get(pn, {})
        c = v22_d.get(pn, {})
        for f in config.FIELDS:
            sa, sb, sc = str(a.get(f)), str(b.get(f)), str(c.get(f))
            if sa == sc and sa != sb:
                # GPT-4o 同 (V12==V22)，V18 不同
                ans_v18 = b.get(f)
                ans_gpt = a.get(f)
                v18_ok = is_correct(ans_v18, exp_rec.get(f), f)
                gpt_ok = is_correct(ans_gpt, exp_rec.get(f), f)
                out["v18_isolated"].append({
                    "part": pn, "field": f,
                    "v12=v22": ans_gpt, "v18": ans_v18, "gt": exp_rec.get(f),
                    "gpt_ok": gpt_ok, "v18_ok": v18_ok,
                })
            elif sa == sb and sa != sc:
                # V12 == V18 ≠ V22
                pass  # not interesting
    return out


train_conflicts = count_conflicts(v12, v18, v22, spec)
print(f"=== Train ===")
print(f"V18 isolated (V12==V22≠V18): {len(train_conflicts['v18_isolated'])} cells")
for info in train_conflicts["v18_isolated"]:
    print(f"  [{info['part']}] {info['field']}")
    print(f"    V12=V22 = {info['v12=v22']!r}  match={info['gpt_ok']}")
    print(f"    V18     = {info['v18']!r}  match={info['v18_ok']}")
    print(f"    GT      = {info['gt']!r}")

# 評估如果這些 conflict 全採 V18，效益多少
v18_correct = sum(1 for c in train_conflicts["v18_isolated"] if c["v18_ok"])
gpt_correct = sum(1 for c in train_conflicts["v18_isolated"] if c["gpt_ok"])
print(f"\n  若全採 V18: {v18_correct} 對 / 若全採 V12=V22: {gpt_correct} 對")
print(f"  best: 全採 V18 vs 全採 V12=V22 = {'V18' if v18_correct > gpt_correct else 'V12=V22'}")
