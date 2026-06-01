"""一次性：算報告引用的各版本在 110格(含PN) 與 100格(排除PN) 的對數。
給改報告當事實基礎，不估計。
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook

PN_FIELD = "Part Number"
spec = load_specbook(config.SPECBOOK_PATH)

CELLS = [
    ("V1 qwen7b 純文字",          "v1_qwen7b"),
    ("V2 GPT-4o 純文字",          "v2_pdfplumber_azure_gpt_4o"),
    ("V12 多模態看圖",            "v12_multimodal_azure_gpt_4o_conservative"),
    ("V23 三模型投票(乾淨上限)",  "v23_majority_vote_3model"),
    ("V26 小封裝視覺偏誤修正",    "v26_triaxis_v18_override"),
    ("V40 尺寸外伸(train最高)",   "v40_lw_outer_combined"),
    ("V44 溫度 grep",             "v44_tj_single_grep_tamb"),
    ("V47 加 swap 保險",          "v47_llama_swap_only"),
    ("整合版(最終成果)",          "v_clean_dim_integrated"),
]


def cell_correct(e, exp, f):
    ext, expv = e.get(f), exp.get(f)
    if f in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, expv, config.NUMERIC_TOLERANCE)
    elif f in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, expv, config.TEXT_MATCH_THRESHOLD)
        return ok
    return cmp_exact(ext, expv)


print(f"{'版本':<26} {'110含PN':>9} {'100排PN':>9} {'PN欄':>6}")
print("-" * 56)
for label, cell_id in CELLS:
    p = config.ARCHIVE_DIR / cell_id / "results.json"
    if not p.exists():
        print(f"{label:<26}  MISSING: {cell_id}")
        continue
    res = json.loads(p.read_text(encoding="utf-8"))
    ok_110 = ok_pn = 0
    for pn, exp in spec.items():
        e = res.get(pn, {})
        for f in config.FIELDS:
            good = ("_error" not in e) and cell_correct(e, exp, f)
            if good:
                ok_110 += 1
                if f == PN_FIELD:
                    ok_pn += 1
    ok_100 = ok_110 - ok_pn
    print(f"{label:<26} {f'{ok_110}/110':>9} {f'{ok_100}/100':>9} {f'{ok_pn}/10':>6}")
