"""讀整合版結果(v_clean_dim_integrated)逐格比對 specbook，印每顆每欄對錯 + 全對顆 + 逐欄統計。
給改報告當事實基礎，不估計。
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook

spec = load_specbook(config.SPECBOOK_PATH)
res = json.loads((config.ARCHIVE_DIR / "v_clean_dim_integrated" / "results.json").read_text(encoding="utf-8"))


def cell_correct(e, exp, f):
    ext, expv = e.get(f), exp.get(f)
    if f in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, expv, config.NUMERIC_TOLERANCE)
    elif f in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, expv, config.TEXT_MATCH_THRESHOLD)
        return ok
    return cmp_exact(ext, expv)


allcorrect = []
total_ok = 0
for pn, exp in spec.items():
    errs = [f for f in config.FIELDS if not cell_correct(e := res.get(pn, {}), exp, f)]
    ok = len(config.FIELDS) - len(errs)
    total_ok += ok
    if not errs:
        allcorrect.append(pn)
    else:
        detail = "; ".join(f"{f}=抽{res.get(pn, {}).get(f)}/答{exp.get(f)}" for f in errs)
        print(f"[{pn}] 11格對{ok}格  錯: {detail}", flush=True)

print(f"\n全對(11/11)的顆: {allcorrect}", flush=True)
print(f"\n逐欄(各10格):", flush=True)
for f in config.FIELDS:
    ok = sum(1 for pn, exp in spec.items() if cell_correct(res.get(pn, {}), exp, f))
    print(f"  10格對{ok}格  {f}", flush=True)
print(f"\n整體: 110格對{total_ok}格", flush=True)
