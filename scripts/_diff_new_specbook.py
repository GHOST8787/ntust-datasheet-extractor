"""新 specbook 下重評 V40/V43/V44/V47 cell-level 對錯"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from reevaluate import (
    cmp_numeric, cmp_exact, cmp_text, load_specbook,
    NUMERIC_TOLERANCE_LOOSE, TEXT_MATCH_THRESHOLD_LOOSE,
)

spec = load_specbook(Path("data/specbook.xlsx"))
fields = [k for k in next(iter(spec.values())).keys() if k != "Part Number"]

for ver_dir in ["v40_lw_outer_combined", "v43_he_ratio_filtered",
                "v44_tj_single_grep_tamb", "v47_llama_swap_only"]:
    path = Path(f"output/_archive/{ver_dir}/results.json")
    if not path.exists():
        print(f"[skip] {ver_dir}")
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    correct = 0
    total = 0
    wrong = []
    for part, gt in spec.items():
        result = data.get(part)
        if not result:
            continue
        extracted = result.get("extracted", result) if isinstance(result, dict) else {}
        for field in fields:
            total += 1
            pred = extracted.get(field)
            truth = gt[field]
            if isinstance(truth, (int, float)):
                ok = cmp_numeric(pred, truth, NUMERIC_TOLERANCE_LOOSE)
            elif field == "PIN Number":
                ok = cmp_exact(pred, truth)
            else:
                ok = cmp_text(pred, truth, TEXT_MATCH_THRESHOLD_LOOSE)
            if ok:
                correct += 1
            else:
                wrong.append((part, field, pred, truth))
    print(f"=== {ver_dir}: {correct}/{total} = {correct/total*100:.1f}% ===")
    for w in wrong:
        print(f"  X {w[0]:12s} | {str(w[1])[:42]:42s} | pred={str(w[2])[:25]:25s} | gt={w[3]}")
    print()
