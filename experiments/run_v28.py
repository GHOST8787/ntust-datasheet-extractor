"""V28 — Narrow override on triple-agreement cells with large divergence

對 V12=V18=V22 三票同意的 L/W/H cells：
  - 若 narrow re-extract 跟 baseline 相對誤差 > 30% → 採 narrow（vision arch 看到三模型 blind spot）
  - 否則 keep baseline

對 V12/V18/V22 有 disagreement 的 cells：
  - 沿用 V26 邏輯（triaxis override + V23 majority）

generic — 不依賴 train set 內容。
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
}
HOLDOUT_DIRS = {k: f"{k}_NEW_PDFS_test" for k in TRAIN.keys()}
DIM = ["Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"]

DIVERGENCE_THRESHOLD = 0.30  # narrow 跟 baseline 相對誤差 > 30% trigger override


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
    if s == -1:
        raise ValueError(f"No JSON: {text[:200]!r}")
    return json.loads(text[s:e + 1])


NARROW_PROMPT = """你是專業電子元件 datasheet 機械尺寸抽取專家。

下方圖片是 cropped 的 Package Outline / Mechanical Drawing 區塊圖。

# 任務
從圖中抽出 **指定型號 {PART_NUMBER}** 的 body L/W/H：
- Maximum Length (mm) = D Max
- Maximum Width (mm) = E Max
- Maximum Height (mm) = A Max

# 硬性規則
1. 永遠取 MAX 欄
2. D→L / E→W / A→H（不論物理大小）
3. 禁用 D2/E1/E2/H_E/L/L1 等變體
4. 單位 mm（inches × 25.4）
5. **不要用 Recommended Land Pattern / Footprint 的數值**
6. 模糊回 null

# JSON 輸出
{{
  "Maximum Length (mm)": <浮點/null>,
  "Maximum Width (mm)": <浮點/null>,
  "Maximum Height (mm)": <浮點/null>
}}

只輸出 JSON。
"""


def narrow_extract(backend, pn: str, pdf_path: Path) -> dict:
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return {}
    images_b64 = [b64 for (_, b64) in crops]
    try:
        raw = backend.call_multimodal(
            NARROW_PROMPT.format(PART_NUMBER=pn),
            images_b64,
            timeout=config.TIMEOUT,
            response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] narrow fail: {e}", flush=True)
        return {}


def relative_diff(a, b):
    """|a - b| / |b|"""
    try:
        af, bf = float(a), float(b)
    except (TypeError, ValueError):
        return float("inf") if str(a) != str(b) else 0.0
    if bf == 0:
        return float("inf") if af != 0 else 0.0
    return abs(af - bf) / abs(bf)


def is_v18_isolated_triaxis(v12_d, v18_d, v22_d, pn):
    for f in DIM:
        a = str(v12_d.get(pn, {}).get(f))
        b = str(v18_d.get(pn, {}).get(f))
        c = str(v22_d.get(pn, {}).get(f))
        if not (a == c and a != b):
            return False
    return True


def merge(sources, narrow):
    out = {}
    parts = set()
    for s in sources.values():
        parts.update(s.keys())
    for pn in parts:
        a = {k: v for k, v in sources["v12"].get(pn, {}).items() if not k.startswith("_")}
        b = {k: v for k, v in sources["v18"].get(pn, {}).items() if not k.startswith("_")}
        c = {k: v for k, v in sources["v22"].get(pn, {}).items() if not k.startswith("_")}
        nw = narrow.get(pn, {})
        triaxis = is_v18_isolated_triaxis(sources["v12"], sources["v18"], sources["v22"], pn)
        merged = {}
        for f in config.FIELDS:
            if triaxis and f in DIM:
                merged[f] = b.get(f)
                continue
            av, bv, cv = a.get(f), b.get(f), c.get(f)
            # V23 majority
            counts = Counter([str(av), str(bv), str(cv)])
            top_str, top_n = counts.most_common(1)[0]
            if top_n >= 2:
                for v in (av, bv, cv):
                    if str(v) == top_str:
                        baseline = v
                        break
            else:
                baseline = av  # fallback

            # 對 L/W/H + narrow available + 全三同意 (top_n=3) → 看 narrow
            if f in DIM and top_n == 3 and f in nw and nw[f] is not None:
                narrow_v = nw[f]
                diff = relative_diff(narrow_v, baseline)
                if diff > DIVERGENCE_THRESHOLD:
                    print(f"  [{pn}] {f}: V28 override baseline={baseline} → narrow={narrow_v} (diff {diff*100:.0f}%)")
                    merged[f] = narrow_v
                    continue
            merged[f] = baseline
        out[pn] = merged
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    train_sources = {k: load_archive(k) for k in ("v12", "v18", "v22")}
    train_narrow = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        if not pdf_path.exists():
            continue
        result = narrow_extract(backend, pn, pdf_path)
        if result:
            train_narrow[pn] = result
            print(f"  [{pn}] narrow: L={result.get(DIM[0])}, W={result.get(DIM[1])}, H={result.get(DIM[2])}")

    train_merged = merge(train_sources, train_narrow)
    train_dir = config.ARCHIVE_DIR / "v28_narrow_divergence_override"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote train: {train_dir}")

    print()
    print("=== Holdout ===")
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
        pdf_path = config.PROJECT_ROOT / rel
        if not pdf_path.exists():
            continue
        result = narrow_extract(backend, pn, pdf_path)
        if result:
            holdout_narrow[pn] = result
            print(f"  [{pn}] narrow: L={result.get(DIM[0])}, W={result.get(DIM[1])}, H={result.get(DIM[2])}")

    holdout_merged = merge(holdout_sources, holdout_narrow)
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v28_narrow_divergence_override_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")

    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
