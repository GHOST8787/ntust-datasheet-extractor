"""V7 K: 用寬鬆容差重評估 V3-V6 各 cell 的 results.json

不重跑 LLM，只重評估比對邏輯：
  - 嚴格容差（main.py 預設）: numeric ±5% / text token-set ≥50%
  - 寬鬆容差（V7 K）        : numeric ±10% / text token-set ≥30%

驗證問題：「我們的比對標準是不是太嚴，分數其實低估了？」

輸出：
  - 主控台印出每 cell 的 strict / loose 對照
  - 寫 markdown 報告附在 V7 報告附錄
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import config

# ---- 寬鬆容差 ----
NUMERIC_TOLERANCE_LOOSE = 0.10  # ±10%（vs main.py ±5%）
TEXT_MATCH_THRESHOLD_LOOSE = 0.30  # ≥30%（vs main.py ≥50%）

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass


# ===================================================================
# 從 main.py 複製的 cmp 邏輯（避免循環 import）
# ===================================================================

def _norm_token(t: str) -> str:
    s = t.lower()
    s = s.replace("μ", "u").replace("µ", "u")
    s = re.sub(r"\b(ta|tj|vr|ir|if|vf|tc|tamb)\s*=\s*\+?", "", s)
    s = re.sub(r"\b(ma|a|v|w)(dc|ac|pk|rms)\b", r"\1", s)
    s = s.replace(",", "").replace("，", "").replace("、", "").replace("+", "").replace("°", "")
    s = re.sub(r"\s+", "", s)

    def strip0(m):
        n = m.group(0)
        if "." in n:
            n = n.rstrip("0").rstrip(".")
        return n

    s = re.sub(r"\d+\.\d+", strip0, s)
    return s


def split_text(v) -> set:
    if v is None or not isinstance(v, str):
        return set()
    return {_norm_token(p) for p in re.split(r"[、]", v) if p.strip()}


def cmp_numeric(x, e, tolerance: float) -> bool:
    if x is None or e is None:
        return x == e
    try:
        ef, xf = float(e), float(x)
    except (ValueError, TypeError):
        return str(x).strip() == str(e).strip()
    if ef == 0:
        return abs(xf) < 1e-6
    return abs(xf - ef) / abs(ef) <= tolerance


def cmp_exact(x, e) -> bool:
    if x is None or e is None:
        return x == e

    def norm(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v).strip()

    return norm(x) == norm(e)


def cmp_text(x, e, threshold: float) -> Tuple[bool, float]:
    es = split_text(e)
    xs = split_text(x)
    if not es:
        return (not xs), (1.0 if not xs else 0.0)
    if not xs:
        return False, 0.0
    score = len(es & xs) / len(es)
    return score >= threshold, score


# ===================================================================
# 載入 specbook（ground truth）
# ===================================================================
import openpyxl

def load_specbook(path: Path) -> Dict[str, Dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    headers = list(rows[0])
    spec = {}
    for r in rows[1:]:
        if not r or r[0] is None:
            continue
        rec = dict(zip(headers, r))
        pn = str(rec.get("Part Number", "")).strip()
        if pn:
            spec[pn] = rec
    return spec


# ===================================================================
# 評估函式（可調容差）
# ===================================================================

def evaluate_with_tolerance(extracted: Dict, spec: Dict, numeric_tol: float, text_threshold: float) -> Dict:
    out = {"overall": {"correct": 0, "total": 0, "accuracy": 0.0}, "per_part": {}}
    for pn, exp_rec in spec.items():
        e = extracted.get(pn, {})
        pr = {"correct": 0, "total": 0}
        if "_error" in e:
            pr["total"] = len(config.FIELDS)
        else:
            for f in config.FIELDS:
                exp = exp_rec.get(f)
                ext = e.get(f)
                if f in config.NUMERIC_FIELDS:
                    ok = cmp_numeric(ext, exp, numeric_tol)
                elif f in config.TEXT_FIELDS:
                    ok, _ = cmp_text(ext, exp, text_threshold)
                else:
                    ok = cmp_exact(ext, exp)
                pr["total"] += 1
                if ok:
                    pr["correct"] += 1
        pr["accuracy"] = pr["correct"] / pr["total"] if pr["total"] else 0
        out["per_part"][pn] = pr
        out["overall"]["correct"] += pr["correct"]
        out["overall"]["total"] += pr["total"]
    if out["overall"]["total"]:
        out["overall"]["accuracy"] = out["overall"]["correct"] / out["overall"]["total"]
    return out


# ===================================================================
# 主流程
# ===================================================================

CELLS_TO_REEVALUATE = [
    ("V2 Mistral baseline", "v2_pdfplumber_azure_mistral_medium_2505"),
    ("V2 GPT-4o baseline", "v2_pdfplumber_azure_gpt_4o"),
    ("V3 A Mistral×Strict", "v3_dual_agent_pdfplumber_azure_mistral_medium_2505_strict"),
    ("V3 B Mistral×Con", "v3_dual_agent_pdfplumber_azure_mistral_medium_2505_conservative"),
    ("V3 C GPT-4o×Strict", "v3_dual_agent_pdfplumber_azure_gpt_4o_strict"),
    ("V3 D GPT-4o×Con", "v3_dual_agent_pdfplumber_azure_gpt_4o_conservative"),
    ("V4 E GPT-4o×Con×MM", "v4_multimodal_azure_gpt_4o_conservative"),
    ("V5 G ×Strict schema", "v5_strict_schema_multimodal_azure_gpt_4o_conservative"),
    ("V6 H ×CoT", "v6_cot_multimodal_azure_gpt_4o_conservative"),
]


def main():
    spec = load_specbook(config.SPECBOOK_PATH)
    print(f"Ground truth: {len(spec)} parts × {len(config.FIELDS)} fields")
    print()
    print(f"{'Cell':<32}  {'Strict (±5%/≥50%)':>20}  {'Loose (±10%/≥30%)':>20}  {'Δ':>8}")
    print("-" * 90)

    results = []
    for label, archive_dir in CELLS_TO_REEVALUATE:
        results_json_path = config.ARCHIVE_DIR / archive_dir / "results.json"
        if not results_json_path.exists():
            print(f"{label:<32}  [MISSING] {results_json_path.name}")
            continue
        with open(results_json_path, encoding="utf-8") as f:
            extracted = json.load(f)

        strict = evaluate_with_tolerance(
            extracted, spec,
            numeric_tol=config.NUMERIC_TOLERANCE,
            text_threshold=config.TEXT_MATCH_THRESHOLD,
        )
        loose = evaluate_with_tolerance(
            extracted, spec,
            numeric_tol=NUMERIC_TOLERANCE_LOOSE,
            text_threshold=TEXT_MATCH_THRESHOLD_LOOSE,
        )

        s_acc = strict["overall"]["accuracy"] * 100
        l_acc = loose["overall"]["accuracy"] * 100
        delta = l_acc - s_acc

        s_str = f"{strict['overall']['correct']}/{strict['overall']['total']} = {s_acc:.1f}%"
        l_str = f"{loose['overall']['correct']}/{loose['overall']['total']} = {l_acc:.1f}%"
        print(f"{label:<32}  {s_str:>20}  {l_str:>20}  {delta:>+7.1f}%")

        results.append({
            "label": label,
            "archive": archive_dir,
            "strict": strict,
            "loose": loose,
            "delta": delta,
        })

    # 寫 markdown 報告片段
    md_path = config.OUTPUT_DIR / "v7_k_loose_tolerance_table.md"
    lines = [
        "# V7 K — 寬鬆容差重評估結果表",
        "",
        f"嚴格容差（main.py 預設）：numeric ±{config.NUMERIC_TOLERANCE*100:.0f}% / text token-set ≥{config.TEXT_MATCH_THRESHOLD*100:.0f}%",
        f"寬鬆容差（V7 K）        ：numeric ±{NUMERIC_TOLERANCE_LOOSE*100:.0f}% / text token-set ≥{TEXT_MATCH_THRESHOLD_LOOSE*100:.0f}%",
        "",
        "| Cell | Strict | Loose | Δ |",
        "|---|---|---|---|",
    ]
    for r in results:
        s = r["strict"]["overall"]
        l = r["loose"]["overall"]
        lines.append(
            f"| {r['label']} | {s['correct']}/{s['total']} = {s['accuracy']*100:.1f}% | "
            f"{l['correct']}/{l['total']} = {l['accuracy']*100:.1f}% | {r['delta']:+.1f}% |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print()
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()
