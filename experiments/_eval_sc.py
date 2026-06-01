"""確認 sc 整合版(v_clean_dim_rules_sc_integrated)逐格對錯 + 印電流欄全 10 顆標答(評估電流規則用)。"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook

spec = load_specbook(config.SPECBOOK_PATH)
res = json.loads((config.ARCHIVE_DIR / "v_clean_dim_rules_sc_integrated" / "results.json").read_text(encoding="utf-8"))
CUR = "I_O、I_F (A)"


def cell_correct(e, exp, f):
    ext, expv = e.get(f), exp.get(f)
    if f in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, expv, config.NUMERIC_TOLERANCE)
    elif f in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, expv, config.TEXT_MATCH_THRESHOLD)
        return ok
    return cmp_exact(ext, expv)


print("=== sc 整合版確切錯格 ===", flush=True)
total_ok = 0
for pn, exp in spec.items():
    errs = [f for f in config.FIELDS if not cell_correct(res.get(pn, {}), exp, f)]
    total_ok += len(config.FIELDS) - len(errs)
    for f in errs:
        print(f"  [{pn}] {f}: 抽 {res.get(pn, {}).get(f)} / 答 {exp.get(f)}", flush=True)
print(f"\n整體: 110 格對 {total_ok} 格", flush=True)

print(f"\n=== 電流欄「{CUR}」全 10 顆標答 vs 抽值 ===", flush=True)
for pn, exp in spec.items():
    print(f"  [{pn}] 答 {exp.get(CUR)}  /  抽 {res.get(pn, {}).get(CUR)}", flush=True)
