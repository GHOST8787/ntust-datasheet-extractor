"""統一評估所有版本的 train_acc + holdout_acc

不重跑 LLM，從以下來源還原各版本結果：
  - train (8 cells specbook)   : output/_archive/<cell_id>/results.json
  - holdout (5 NEW PDFs)        : output/iteration_logs/<cell_id>_NEW_PDFS_test/*.jsonl 內 event=final

輸出：
  output/baseline_table.md   人類可讀的對照表
  output/baseline_table.json 機器可讀的完整數字
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config
from reevaluate import (
    cmp_numeric, cmp_exact, cmp_text, load_specbook,
    NUMERIC_TOLERANCE_LOOSE, TEXT_MATCH_THRESHOLD_LOOSE,
)
from evaluate_new_5 import GROUND_TRUTH as HOLDOUT_GT


VERSIONS = [
    ("V2 GPT-4o baseline",         "v2_pdfplumber_azure_gpt_4o"),
    ("V2 Mistral baseline",        "v2_pdfplumber_azure_mistral_medium_2505"),
    ("V3 D GPT-4o dual×Con",       "v3_dual_agent_pdfplumber_azure_gpt_4o_conservative"),
    ("V4 E GPT-4o MM×Con",         "v4_multimodal_azure_gpt_4o_conservative"),
    ("V5 G strict schema",         "v5_strict_schema_multimodal_azure_gpt_4o_conservative"),
    ("V6 H CoT",                   "v6_cot_multimodal_azure_gpt_4o_conservative"),
    ("V8",                         "v8_multimodal_azure_gpt_4o_conservative"),
    ("V9",                         "v9_multimodal_azure_gpt_4o_conservative"),
    ("V10",                        "v10_multimodal_azure_gpt_4o_conservative"),
    ("V11",                        "v11_multimodal_azure_gpt_4o_conservative"),
    ("V12",                        "v12_multimodal_azure_gpt_4o_conservative"),
    ("V13",                        "v13_multimodal_azure_gpt_4o_conservative"),
    ("V14 MM critic",              "v14_multimodal_azure_gpt_4o_conservative"),
    ("V15 strict critic",          "v15_multimodal_azure_gpt_4o_strict"),
    ("V16 hybrid critic",          "v16_multimodal_azure_gpt_4o_hybrid"),
    ("V17 temp=0.5",               "v17_multimodal_azure_gpt_4o_conservative"),
    ("V18 Llama-4-Maverick",       "v18_multimodal_azure_llama_4_maverick_conservative"),
    ("V19 ensemble",               "v19_ensemble"),
    ("V20 zoom=4.5 + precision",   "v20_multimodal_azure_gpt_4o_conservative"),
    ("V21 crop dimension redo",    "v21_crop_dimension_redo"),
    ("V22 toc extractor",          "v22_multimodal_toc_azure_gpt_4o_conservative"),
    ("V23 3-model majority",       "v23_majority_vote_3model"),
    ("V24 8-model majority",       "v24_majority_vote_8model"),
    ("V25 cluster-aware vote",     "v25_cluster_aware_vote"),
    ("V26 triaxis V18 override",   "v26_triaxis_v18_override"),
    ("V27 narrow 4-way",           "v27_narrow_4way"),
    ("V28 narrow divergence",      "v28_narrow_divergence_override"),
    ("V29 V12+Tj+IO prompt",       "v29_multimodal_azure_gpt_4o_conservative"),
    ("V30 V29+V26 logic",          "v30_v29_with_v26_logic"),
    ("V31 V26+V29 2-field ovr",    "v31_v26_with_v29_2field_override"),
    ("V32 V31+Tj regex",           "v32_v31_tj_postprocess"),
    ("V33 V31+Tj LLM query",       "v33_v31_tj_llm_query"),
    ("V34 V31+verify-all",         "v34_v31_with_verify"),
    ("V35 4-way w/ V29",           "v35_4way_vote_with_v29"),
    ("V36 V31+Llama critic",       "v36_v31_with_llama_critic"),
    ("V37 L=max(D,E) swap",        "v37_lw_max_swap"),
    ("V38 W=H_E override",         "v38_w_he_override"),
    ("V39 L_outer override",       "v39_l_outer_override"),
    ("V40 LW outer combined",      "v40_lw_outer_combined"),
    ("V41 Tj single + no Tamb",    "v41_tj_single_no_tamb"),
    ("V42 Tj regex Tamb",          "v42_tj_regex_tamb"),
    ("V43 H_E filtered",           "v43_he_ratio_filtered"),
    ("V44 Tj+grep Tamb",           "v44_tj_single_grep_tamb"),
    ("V45 WH anomaly redo",        "v45_wh_anomaly_redo"),
    ("V46 Llama WH redo",          "v46_llama_wh_redo"),
    ("V47 Llama swap only",        "v47_llama_swap_only"),
    ("V48 H_E multi-sample",       "v48_he_multi_sample"),
]


def cell_correct(extracted: Dict, exp_rec: Dict, field: str, numeric_tol: float, text_threshold: float) -> bool:
    ext = extracted.get(field)
    exp = exp_rec.get(field)
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, exp, numeric_tol)
    elif field in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, exp, text_threshold)
        return ok
    else:
        return cmp_exact(ext, exp)


def evaluate(extracted: Dict, gt: Dict, numeric_tol: float, text_threshold: float) -> Dict:
    correct = 0
    total = 0
    per_field_err: Dict[str, int] = {}
    for pn, exp_rec in gt.items():
        e = extracted.get(pn, {})
        if "_error" in e:
            total += len(config.FIELDS)
            for f in config.FIELDS:
                per_field_err[f] = per_field_err.get(f, 0) + 1
            continue
        for f in config.FIELDS:
            total += 1
            if cell_correct(e, exp_rec, f, numeric_tol, text_threshold):
                correct += 1
            else:
                per_field_err[f] = per_field_err.get(f, 0) + 1
    return {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0,
        "per_field_errors": per_field_err,
    }


def load_train_results(cell_id: str) -> Dict:
    p = config.ARCHIVE_DIR / cell_id / "results.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def load_holdout_results(cell_id: str) -> Dict:
    """從 iteration_logs/<cell_id>_NEW_PDFS_test/*.jsonl 還原 final answer"""
    log_dir = config.OUTPUT_DIR / "iteration_logs" / f"{cell_id}_NEW_PDFS_test"
    if not log_dir.exists():
        return {}
    out = {}
    for jsonl_path in log_dir.glob("*.jsonl"):
        part = jsonl_path.stem
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                try:
                    evt = json.loads(line)
                except Exception:
                    continue
                if evt.get("event") == "final":
                    out[part] = evt.get("final_answer", {})
                    break
    return out


def find_actual_cell_id(version_base: str) -> str:
    """從 archive 找實際的 cell_id（因為 v18 用 llama 後綴，v19 直接是 v19_ensemble）"""
    if (config.ARCHIVE_DIR / version_base).exists():
        return version_base
    # 嘗試 prefix match
    candidates = [d.name for d in config.ARCHIVE_DIR.iterdir() if d.is_dir() and d.name.startswith(version_base.split("_")[0] + "_")]
    return candidates[0] if candidates else version_base


def find_actual_holdout_cell_id(version_base: str) -> str:
    """NEW_PDFS_test 的 cell_id — 從 iteration_logs 找對應 prefix"""
    log_root = config.OUTPUT_DIR / "iteration_logs"
    # 先直接試
    direct = f"{version_base}_NEW_PDFS_test"
    if (log_root / direct).exists():
        return version_base
    # 嘗試 prefix match (v18 用 llama suffix 寫到 _archive 但 NEW_PDFS_test 用統一 prefix)
    prefix = version_base.split("_")[0]  # v12, v18 etc
    candidates = [d.name for d in log_root.iterdir() if d.is_dir() and d.name.startswith(f"{prefix}_NEW_PDFS_test")]
    if candidates:
        return candidates[0].replace("_NEW_PDFS_test", "")
    # 完整 cell_id match (e.g. v18_multimodal_azure_llama_4_maverick_conservative_NEW_PDFS_test)
    candidates2 = [d.name for d in log_root.iterdir() if d.is_dir() and d.name.startswith(f"{version_base}_NEW_PDFS_test")]
    return candidates2[0].replace("_NEW_PDFS_test", "") if candidates2 else version_base


def main():
    spec = load_specbook(config.SPECBOOK_PATH)
    train_n = len(spec) * len(config.FIELDS)
    holdout_n = len(HOLDOUT_GT) * len(config.FIELDS)
    print(f"Train set:   {len(spec)} parts × {len(config.FIELDS)} fields = {train_n} cells")
    print(f"Holdout set: {len(HOLDOUT_GT)} parts × {len(config.FIELDS)} fields = {holdout_n} cells")
    print()
    print(f"{'Version':<30} {'Train (strict)':>16} {'Holdout (strict)':>18} {'Gap':>8} {'OverfitFlag':>12}")
    print("-" * 90)

    rows = []
    for label, base in VERSIONS:
        # Train
        archive_cell = find_actual_cell_id(base)
        train_data = load_train_results(archive_cell)
        if not train_data:
            print(f"{label:<30}  [MISSING train: {archive_cell}]")
            continue
        train = evaluate(train_data, spec, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD)

        # Holdout
        holdout_cell = find_actual_holdout_cell_id(base)
        holdout_data = load_holdout_results(holdout_cell)
        if holdout_data:
            holdout = evaluate(holdout_data, HOLDOUT_GT, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD)
        else:
            holdout = None

        train_str = f"{train['correct']}/{train['total']} = {train['accuracy']*100:.1f}%"
        if holdout:
            holdout_str = f"{holdout['correct']}/{holdout['total']} = {holdout['accuracy']*100:.1f}%"
            gap = train['accuracy'] - holdout['accuracy']
            gap_str = f"{gap*100:+.1f}%"
            # Overfit 判定：gap > 15% 或 holdout < V4 E baseline (80%)
            v4e_holdout = 0.80
            flag = "OK"
            reasons = []
            if gap > 0.15:
                reasons.append(f"gap>{15}%")
            if holdout['accuracy'] < v4e_holdout:
                reasons.append(f"holdout<{v4e_holdout*100:.0f}%")
            if reasons:
                flag = "OVERFIT(" + ",".join(reasons) + ")"
        else:
            holdout_str = "[no log]"
            gap_str = "—"
            flag = "—"

        print(f"{label:<30} {train_str:>16} {holdout_str:>18} {gap_str:>8} {flag:>12}")
        rows.append({
            "label": label,
            "cell_id_train": archive_cell,
            "cell_id_holdout": holdout_cell,
            "train": train,
            "holdout": holdout,
            "overfit_flag": flag,
        })

    # ---- markdown 報告 ----
    md_lines = [
        "# Baseline Table — Train + Holdout 對照",
        "",
        f"- **Train set**: 10 parts × 11 fields = {train_n} cells（specbook.xlsx）",
        f"- **Holdout set**: 5 NEW PDFs × 11 fields = {holdout_n} cells（evaluate_new_5.py GROUND_TRUTH，手動標）",
        "- **Strict 容差**: numeric ±5% / text token-set ≥ 50%",
        "- **Overfit 判定**: gap > 15% **或** holdout_acc < V4 E baseline (80%)",
        "",
        "| Version | Train | Holdout | Gap | Flag |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        t = r["train"]
        h = r["holdout"]
        train_str = f"{t['correct']}/{t['total']} = **{t['accuracy']*100:.1f}%**"
        if h:
            holdout_str = f"{h['correct']}/{h['total']} = **{h['accuracy']*100:.1f}%**"
            gap = (t['accuracy'] - h['accuracy']) * 100
            gap_str = f"{gap:+.1f}%"
        else:
            holdout_str = "—"
            gap_str = "—"
        md_lines.append(f"| {r['label']} | {train_str} | {holdout_str} | {gap_str} | {r['overfit_flag']} |")

    md_lines.append("")
    md_lines.append("## 每欄位錯誤分佈（取 best train 版本）")
    md_lines.append("")
    # 找 train_acc 最高的版本
    best_row = max(rows, key=lambda r: r["train"]["accuracy"])
    md_lines.append(f"Best train version: **{best_row['label']}** = {best_row['train']['accuracy']*100:.1f}%")
    md_lines.append("")
    md_lines.append("| Field | Train 錯誤數 | Holdout 錯誤數 |")
    md_lines.append("|---|---|---|")
    for f in config.FIELDS:
        t_err = best_row["train"]["per_field_errors"].get(f, 0)
        h_err = best_row["holdout"]["per_field_errors"].get(f, 0) if best_row["holdout"] else "—"
        md_lines.append(f"| `{f}` | {t_err} | {h_err} |")

    out_md = config.OUTPUT_DIR / "baseline_table.md"
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    out_json = config.OUTPUT_DIR / "baseline_table.json"
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print()
    print(f"Wrote: {out_md}")
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()
