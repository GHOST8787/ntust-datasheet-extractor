"""算 V12 (GPT-4o) ∪ V18 (Llama) ensemble upper bound

對每元件每欄位：V12 對 OR V18 對 → 算對
這代表「假設有完美 critic 能挑對的 那一個」的理論上限。

如果 upper bound >= 95% → 值得做實際 ensemble 機制
如果 upper bound < 95% → ensemble 也救不了，89.7% 真的是天花板
"""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook
from evaluate_new_5 import GROUND_TRUTH as NEW_GT


V12_ARCHIVE = "v12_multimodal_azure_gpt_4o_conservative"
V18_ARCHIVE = "v18_multimodal_azure_llama_4_maverick_conservative"


def cell_correct(extracted, exp_rec, field, numeric_tol, text_threshold):
    ext = extracted.get(field)
    exp = exp_rec.get(field)
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, exp, numeric_tol)
    elif field in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, exp, text_threshold)
        return ok
    else:
        return cmp_exact(ext, exp)


def ensemble(a_extracted, b_extracted, gt, numeric_tol, text_threshold):
    """對每 cell 取 max(a 對, b 對)"""
    a_correct = 0
    b_correct = 0
    union_correct = 0
    intersection_correct = 0
    total = 0
    per_part = {}
    diff_cells = []  # a 對 b 錯 OR 反之

    for pn, exp_rec in gt.items():
        a_rec = a_extracted.get(pn, {})
        b_rec = b_extracted.get(pn, {})
        a_err = "_error" in a_rec
        b_err = "_error" in b_rec
        part_total = 0
        part_union = 0
        for f in config.FIELDS:
            part_total += 1
            total += 1
            a_ok = (not a_err) and cell_correct(a_rec, exp_rec, f, numeric_tol, text_threshold)
            b_ok = (not b_err) and cell_correct(b_rec, exp_rec, f, numeric_tol, text_threshold)
            if a_ok:
                a_correct += 1
            if b_ok:
                b_correct += 1
            if a_ok or b_ok:
                union_correct += 1
                part_union += 1
            if a_ok and b_ok:
                intersection_correct += 1
            if a_ok != b_ok:
                diff_cells.append({
                    "part": pn,
                    "field": f,
                    "a_val": a_rec.get(f) if not a_err else "_error",
                    "b_val": b_rec.get(f) if not b_err else "_error",
                    "expected": exp_rec.get(f),
                    "a_ok": a_ok,
                    "b_ok": b_ok,
                })
        per_part[pn] = {"union": part_union, "total": part_total}

    return {
        "a_correct": a_correct,
        "b_correct": b_correct,
        "union_correct": union_correct,
        "intersection_correct": intersection_correct,
        "total": total,
        "per_part": per_part,
        "diff_cells": diff_cells,
    }


def main():
    # ===== 原 10 顆 =====
    spec = load_specbook(config.SPECBOOK_PATH)
    v12_orig = json.loads((config.ARCHIVE_DIR / V12_ARCHIVE / "results.json").read_text(encoding="utf-8"))
    v18_orig = json.loads((config.ARCHIVE_DIR / V18_ARCHIVE / "results.json").read_text(encoding="utf-8"))

    orig = ensemble(v12_orig, v18_orig, spec, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD)

    print("=" * 80)
    print("原 10 顆（自家 ground truth）")
    print("=" * 80)
    print(f"V12 (GPT-4o):    {orig['a_correct']}/{orig['total']} = {orig['a_correct']/orig['total']*100:.1f}%")
    print(f"V18 (Llama):     {orig['b_correct']}/{orig['total']} = {orig['b_correct']/orig['total']*100:.1f}%")
    print(f"交集 (V12 ∩ V18): {orig['intersection_correct']}/{orig['total']} = {orig['intersection_correct']/orig['total']*100:.1f}%")
    print(f"⭐ 聯集 (V12 ∪ V18, upper bound): {orig['union_correct']}/{orig['total']} = {orig['union_correct']/orig['total']*100:.1f}%")
    print()
    print("Per-part union scores:")
    for pn, pr in orig["per_part"].items():
        print(f"  {pn:<15} {pr['union']:>3}/{pr['total']:>3} = {pr['union']/pr['total']*100:>5.1f}%")
    print()
    print(f"差異 cells（V12 vs V18 不同對錯）: {len(orig['diff_cells'])}")
    for c in orig["diff_cells"][:20]:  # 印前 20 個
        winner = "V12" if c["a_ok"] else "V18"
        print(f"  [{c['part']:<15}] {c['field'][:35]:<35} winner={winner}  expected={c['expected']!r:<30} V12={c['a_val']!r:<25} V18={c['b_val']!r}")
    print()

    # ===== 新 5 顆 =====
    v12_new_path = config.ARCHIVE_DIR / V12_ARCHIVE / "new_pdfs_extracted.json"
    # V12 跑 new pdfs 跟原 10 顆同時嗎? extract_new_pdfs.py 寫 output/new_pdfs_extracted.json (一直被覆蓋)
    # V12 archive 內可能沒有 new_pdfs (only main.py results.json)
    # 改成 直接讀 output/new_pdfs_extracted.json (V18 最後寫的)
    # 算 V18 新 5 顆 vs ground truth — 比較沒意義因為 V12 new 5 顆 archive 不在那
    # 簡化：只算原 10 顆 ensemble upper bound
    print("新 5 顆 ensemble: skipped (new_pdfs_extracted.json 每跑被覆蓋，無 V12 留存)")


if __name__ == "__main__":
    main()
