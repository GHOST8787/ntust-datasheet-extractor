"""V19 ensemble — 對 V12 (GPT-4o) 跟 V18 (Llama) 不一致的 cells，用 GPT-4o multimodal critic 看圖判定

不重跑 extraction（V12/V18 archive 已有）。
只對「V12 != V18」的 cells 跑 ensemble critic。

預期：拉到 ensemble upper bound 88.2%（如果 critic 全挑對）
最差：跟 V12 同分 84.5%（如果 critic 全挑錯）
"""
import json
import os
import sys
import time
from pathlib import Path

# 設環境讓 import 不爆
os.environ.setdefault("BACKEND", "azure_gpt4o")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook
from llm_backend import get_backend
from pdf_extractor import MultiModalExtractor

V12_ARCHIVE = "v12_multimodal_azure_gpt_4o_conservative"
V18_ARCHIVE = "v18_multimodal_azure_llama_4_maverick_conservative"


ENSEMBLE_CRITIC_PROMPT = """你是 ensemble 判定員。兩個 LLM (GPT-4o 跟 Llama) 對同一 PDF 抽出 datasheet 規格，**對某個欄位給出不同答案**。

你的任務：對照原始 PDF 文字 + 機械頁截圖，**選出對的那個答案**（或如果都不對，給正確答案）。

# 指定型號
Part Number: {PART_NUMBER}

# 爭議欄位
{FIELD_NAME}

# GPT-4o 答案
{V12_ANSWER}

# Llama 答案
{V18_ANSWER}

# datasheet 純文字（部分）
{PDF_TEXT}

請輸出 JSON：
{{
  "chosen": "v12" | "v18" | "neither",
  "correct_value": <對的值> (如果 chosen=neither 才需要),
  "reason": "<簡短理由 50 字內>"
}}

只輸出 JSON，前後不要文字。"""


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


def find_diff_cells(v12, v18, gt):
    """找 V12 跟 V18 答案不同的 cells"""
    diffs = []
    for pn, exp_rec in gt.items():
        a = v12.get(pn, {})
        b = v18.get(pn, {})
        if "_error" in a or "_error" in b:
            continue
        for f in config.FIELDS:
            av = a.get(f)
            bv = b.get(f)
            # 用簡單字串比對找差異（容差比對留給 evaluate）
            if str(av) != str(bv):
                diffs.append({
                    "part": pn,
                    "field": f,
                    "v12_val": av,
                    "v18_val": bv,
                    "expected": exp_rec.get(f),
                })
    return diffs


def main():
    spec = load_specbook(config.SPECBOOK_PATH)
    v12 = json.loads((config.ARCHIVE_DIR / V12_ARCHIVE / "results.json").read_text(encoding="utf-8"))
    v18 = json.loads((config.ARCHIVE_DIR / V18_ARCHIVE / "results.json").read_text(encoding="utf-8"))

    diffs = find_diff_cells(v12, v18, spec)
    print(f"找到 {len(diffs)} 個 V12 vs V18 差異 cells")
    print()

    # 對每個 diff cell 跑 GPT-4o critic（multimodal）判定
    backend = get_backend()  # azure_gpt4o
    extractor = MultiModalExtractor()

    # 快取 PDF text + images（同顆元件重複用）
    pdf_cache = {}

    decisions = {}
    for i, diff in enumerate(diffs, 1):
        pn = diff["part"]
        f = diff["field"]
        print(f"[{i}/{len(diffs)}] {pn} / {f}", flush=True)
        print(f"  V12={diff['v12_val']!r}, V18={diff['v18_val']!r}, expected={diff['expected']!r}", flush=True)

        # 拿 PDF text + images
        if pn not in pdf_cache:
            pdf_path = config.DATASHEETS_DIR / config.PART_TO_PDF[pn]
            text, images, _ = extractor.extract_with_images(pdf_path)
            pdf_cache[pn] = (text[:6000], images)  # text 限 6K 避免 token 爆
        text, images = pdf_cache[pn]

        prompt = ENSEMBLE_CRITIC_PROMPT.format(
            PART_NUMBER=pn,
            FIELD_NAME=f,
            V12_ANSWER=json.dumps(diff["v12_val"], ensure_ascii=False),
            V18_ANSWER=json.dumps(diff["v18_val"], ensure_ascii=False),
            PDF_TEXT=text,
        )

        try:
            raw = backend.call_multimodal(
                prompt, images,
                timeout=config.TIMEOUT,
                response_format={"type": "json_object"},
            )
            parsed = json.loads(raw)
            chosen = parsed.get("chosen", "v12")
            decisions[(pn, f)] = chosen
            print(f"  → critic 選 {chosen}: {parsed.get('reason', '')[:80]}", flush=True)
        except Exception as e:
            print(f"  → critic error: {e}, fallback v12", flush=True)
            decisions[(pn, f)] = "v12"

    # 合併 ensemble 結果
    ensemble_result = {}
    for pn in spec.keys():
        a = v12.get(pn, {})
        b = v18.get(pn, {})
        if "_error" in a:
            ensemble_result[pn] = a
            continue
        merged = {}
        for f in config.FIELDS:
            if str(a.get(f)) == str(b.get(f)):
                merged[f] = a.get(f)
            else:
                # 差異 cell — 用 critic 決定
                chosen = decisions.get((pn, f), "v12")
                if chosen == "v18":
                    merged[f] = b.get(f)
                else:
                    merged[f] = a.get(f)
        ensemble_result[pn] = merged

    # 算 ensemble 分數
    correct = 0
    total = 0
    per_part = {}
    for pn, exp_rec in spec.items():
        e = ensemble_result.get(pn, {})
        pc = pt = 0
        if "_error" in e:
            pt = len(config.FIELDS)
        else:
            for f in config.FIELDS:
                pt += 1
                if cell_correct(e, exp_rec, f, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD):
                    pc += 1
        correct += pc
        total += pt
        per_part[pn] = (pc, pt)

    print()
    print("=" * 80)
    print(f"V19 Ensemble 結果：{correct}/{total} = {correct/total*100:.1f}%")
    print("=" * 80)
    for pn, (pc, pt) in per_part.items():
        print(f"  {pn:<15} {pc:>3}/{pt:>3} = {pc/pt*100:>5.1f}%")

    # 存 ensemble result
    out_path = config.OUTPUT_DIR / "_archive" / "v19_ensemble" / "results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(ensemble_result, ensure_ascii=False, indent=2), encoding="utf-8")
    # 也存 decisions log
    decisions_log = [
        {"part": k[0], "field": k[1], "chosen": v}
        for k, v in decisions.items()
    ]
    (out_path.parent / "ensemble_decisions.json").write_text(
        json.dumps(decisions_log, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print()
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
