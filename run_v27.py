"""V27 — Narrow per-field re-extract on disagreement cells

對 V26 baseline 的 cells 中，**任何 V12/V18/V22 不一致的 cells** 跑 narrow LLM call
用 cropped 圖 + 「只問該欄位」的 narrow prompt 重抽，當作第 4 票加入投票。

最終答案 = (V12, V18, V22, V27_narrow) 4-way majority + V26 triaxis override 規則。

generic — 不依賴 train set 內容（任何 disagreement cell 都走同樣 narrow flow）。
"""
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

os.environ.setdefault("BACKEND", "azure_gpt4o")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

import config
from llm_backend import get_backend
from crop_extractor import get_dimension_crops


TRAIN = {
    "v12": "v12_multimodal_azure_gpt_4o_conservative",
    "v18": "v18_multimodal_azure_llama_4_maverick_conservative",
    "v22": "v22_multimodal_toc_azure_gpt_4o_conservative",
    "v26": "v26_triaxis_v18_override",
}

HOLDOUT_DIRS = {k: f"{k}_NEW_PDFS_test" for k in TRAIN.keys()}

DIMENSION_FIELDS = ["Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"]


def load_archive(name):
    return json.loads((config.ARCHIVE_DIR / TRAIN[name] / "results.json").read_text(encoding="utf-8"))


def load_holdout(name):
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / HOLDOUT_DIRS[name]
    if not d.exists():
        return out
    for jp in d.glob("*.jsonl"):
        with open(jp, encoding="utf-8") as f:
            for line in f:
                try:
                    evt = json.loads(line)
                except Exception:
                    continue
                if evt.get("event") == "final":
                    out[jp.stem] = evt.get("final_answer", {})
                    break
    return out


def parse_json_lenient(text):
    text = text.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.lower().startswith("json"):
            text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        raise ValueError(f"No JSON: {text[:200]!r}")
    return json.loads(text[s:e + 1])


def has_disagreement(v12_d, v18_d, v22_d, pn, field):
    a = v12_d.get(pn, {}).get(field)
    b = v18_d.get(pn, {}).get(field)
    c = v22_d.get(pn, {}).get(field)
    return not (str(a) == str(b) == str(c))


NARROW_DIM_PROMPT = """你是專業電子元件 datasheet 機械尺寸抽取專家。

下方提供裁剪的 Package Outline / Mechanical Drawing 區塊圖（已 crop 到含尺寸表 + 圖示）。

# 任務
從圖中抽出 **指定型號 {PART_NUMBER}** 的所有 body 尺寸：
- Maximum Length (mm) = D Max
- Maximum Width (mm) = E Max
- Maximum Height (mm) = A Max

# 硬性規則
1. 永遠取 MAX 欄（不是 NOM/TYP/MIN）
2. D→Length / E→Width / A→Height（**不論物理上哪個大**）
3. 禁用 D2/E1/E2/H_E/L/L1 等變體當 L/W/H
4. 單位 mm（inches × 25.4）
5. **若圖含 Recommended Land Pattern / Footprint**，禁用其數值
6. 圖太模糊回 null

# 輸出 JSON
{{
  "Maximum Length (mm)": <浮點 或 null>,
  "Maximum Width (mm)": <浮點 或 null>,
  "Maximum Height (mm)": <浮點 或 null>
}}

只輸出 JSON，前後不要文字。
"""


def narrow_dim_extract(backend, pn: str, pdf_path: Path) -> dict:
    """對單一 part 跑 narrow dimension extract，回 dict 含 3 欄"""
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return {}
    images_b64 = [b64 for (_, b64) in crops]
    prompt = NARROW_DIM_PROMPT.format(PART_NUMBER=pn)
    try:
        raw = backend.call_multimodal(
            prompt, images_b64,
            timeout=config.TIMEOUT,
            response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] narrow fail: {e}", flush=True)
        return {}


def majority_4(values, baseline):
    """4-way majority: ≥3 同意，或 ≥2 majority；否則 baseline"""
    str_values = [str(v) for v in values]
    counts = Counter(str_values)
    top_str, top_n = counts.most_common(1)[0]
    if top_n >= 2:  # 至少 2/4 同意
        for v in values:
            if str(v) == top_str:
                return v
    return baseline


def is_v18_isolated_triaxis(v12_d, v18_d, v22_d, pn):
    for f in DIMENSION_FIELDS:
        a = str(v12_d.get(pn, {}).get(f))
        b = str(v18_d.get(pn, {}).get(f))
        c = str(v22_d.get(pn, {}).get(f))
        if not (a == c and a != b):
            return False
    return True


def merge(sources, narrow_results, part_to_pdf):
    """sources = {v12, v18, v22}, narrow_results = {part: {field: val}}"""
    out = {}
    parts = set()
    for s in sources.values():
        parts.update(s.keys())
    for pn in parts:
        a = {k: v for k, v in sources["v12"].get(pn, {}).items() if not k.startswith("_")}
        b = {k: v for k, v in sources["v18"].get(pn, {}).items() if not k.startswith("_")}
        c = {k: v for k, v in sources["v22"].get(pn, {}).items() if not k.startswith("_")}
        nw = narrow_results.get(pn, {})

        triaxis = is_v18_isolated_triaxis(sources["v12"], sources["v18"], sources["v22"], pn)
        merged = {}
        for f in config.FIELDS:
            if triaxis and f in DIMENSION_FIELDS:
                # V26 override
                merged[f] = b.get(f)
            elif f in DIMENSION_FIELDS and f in nw:
                # 4-way vote: V12, V18, V22, narrow
                merged[f] = majority_4([a.get(f), b.get(f), c.get(f), nw.get(f)], a.get(f))
            else:
                # 3-way V23 majority
                merged[f] = majority_4([a.get(f), b.get(f), c.get(f)], a.get(f))
        out[pn] = merged
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    # === Train: 跑 narrow re-extract on parts ===
    print("=== Train: narrow re-extract on parts with disagreement ===")
    train_sources = {k: load_archive(k) for k in ("v12", "v18", "v22")}

    train_narrow = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        # 只對 L/W/H 有任何 disagreement 的 part 跑
        has_disagree = any(
            has_disagreement(train_sources["v12"], train_sources["v18"], train_sources["v22"], pn, f)
            for f in DIMENSION_FIELDS
        )
        if not has_disagree:
            print(f"  [{pn}] all agree on L/W/H, skip")
            continue
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        if not pdf_path.exists():
            continue
        print(f"  [{pn}] narrow re-extract...")
        result = narrow_dim_extract(backend, pn, pdf_path)
        if result:
            train_narrow[pn] = result
            print(f"    → L={result.get('Maximum Length (mm)')}, W={result.get('Maximum Width (mm)')}, H={result.get('Maximum Height (mm)')}")

    train_merged = merge(train_sources, train_narrow, config.PART_TO_PDF)
    train_dir = config.ARCHIVE_DIR / "v27_narrow_4way"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote train: {train_dir}")

    # === Holdout ===
    print()
    print("=== Holdout: narrow re-extract ===")
    holdout_sources = {k: load_holdout(k) for k in ("v12", "v18", "v22")}
    HOLDOUT_PDFS = [
        ("FFSH5065B",     r"AA\FFSH5065B-F085-D.PDF"),
        ("FFSD1065B",     r"AA\FFSD1065B-D.PDF"),
        ("VS3C20ET07T",   r"AA\vs-3c20et07t-m3.pdf"),
        ("VS3C12ET07S2L", r"AA\vs-3c12et07s2l-m.pdf"),
        ("ASA006V065F4",  r"AA\ASA006V065F4.pdf"),
    ]
    holdout_narrow = {}
    for pn, rel in HOLDOUT_PDFS:
        has_disagree = any(
            has_disagreement(holdout_sources["v12"], holdout_sources["v18"], holdout_sources["v22"], pn, f)
            for f in DIMENSION_FIELDS
        )
        if not has_disagree:
            print(f"  [{pn}] all agree on L/W/H, skip")
            continue
        pdf_path = config.PROJECT_ROOT / rel
        if not pdf_path.exists():
            continue
        print(f"  [{pn}] narrow re-extract...")
        result = narrow_dim_extract(backend, pn, pdf_path)
        if result:
            holdout_narrow[pn] = result
            print(f"    → L={result.get('Maximum Length (mm)')}, W={result.get('Maximum Width (mm)')}, H={result.get('Maximum Height (mm)')}")

    holdout_merged = merge(holdout_sources, holdout_narrow, dict(HOLDOUT_PDFS))
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v27_narrow_4way_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")

    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
