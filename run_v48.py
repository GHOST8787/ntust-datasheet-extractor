"""V48 — V47 + multi-sample H_E query for W-anomaly parts

對 W/L < 0.65 (W 偏小) 且 W < 2.0 (小封裝) 跑 3 次 LLM H_E query 取 median，
ratio 條件放寬到 1.4 ~ 2.0（包含 BAV99W 1.92 ratio）

避免傷害 1N4148W：V40 已對 1N4148W W=1.85 OK。其 ratio 2.09 > 2.0 排除。

generic — 對所有 W 偏小 part 同樣跑
"""
import base64
import json
import os
import statistics
import sys
import time
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


L_KEY = "Maximum Length (mm)"
W_KEY = "Maximum Width (mm)"


HE_PROMPT = """看 cropped Package Outline 圖。找 H_E Max 數字（lead-to-lead 含外伸 lead 的總跨距，比 body E 大）。

# JSON
{{"H_E_max": <浮點/null>}}

只 JSON。Part {PART_NUMBER}, sample {N}.
"""


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
        raise ValueError
    return json.loads(text[s:e + 1])


def load_v47_train():
    return json.loads((config.ARCHIVE_DIR / "v47_llama_swap_only" / "results.json").read_text(encoding="utf-8"))


def load_v47_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v47_llama_swap_only_NEW_PDFS_test"
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


def query_he_n_times(backend, pn, pdf_path, n=3):
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        return []
    images = [b for (_, b) in crops]
    samples = []
    for i in range(n):
        try:
            raw = backend.call_multimodal(
                HE_PROMPT.format(PART_NUMBER=pn, N=i + 1), images,
                timeout=config.TIMEOUT, response_format={"type": "json_object"},
            )
            info = parse_json_lenient(raw)
            v = info.get("H_E_max")
            if v is not None:
                try:
                    samples.append(float(v))
                except (TypeError, ValueError):
                    pass
        except Exception:
            pass
    return samples


def needs_check(baseline):
    """W/L < 0.65 AND L < 4 (小封裝)"""
    try:
        l = float(baseline[L_KEY])
        w = float(baseline[W_KEY])
    except (TypeError, ValueError, KeyError):
        return False
    return (w / l < 0.65) and (l < 4.0)


def apply_override(baseline, pn, he_samples):
    if not he_samples:
        return baseline
    he_median = statistics.median(he_samples)
    cur_w = baseline.get(W_KEY)
    cur_l = baseline.get(L_KEY)
    try:
        cwf, clf = float(cur_w), float(cur_l)
    except (TypeError, ValueError):
        return baseline
    if cwf == 0:
        return baseline
    ratio = he_median / cwf
    if not (ratio > 1.4 and ratio <= 2.0):
        return baseline
    out = dict(baseline)
    print(f"  [{pn}] W: {cur_w} → {he_median} (H_E median of {he_samples}, ratio={ratio:.2f})")
    out[W_KEY] = he_median
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v47 = load_v47_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v47.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        if not needs_check(baseline):
            train_merged[pn] = baseline
            continue
        print(f"  [{pn}] checking H_E samples (W/L={float(baseline[W_KEY])/float(baseline[L_KEY]):.2f}, L={baseline[L_KEY]})")
        samples = query_he_n_times(backend, pn, pdf_path)
        print(f"    samples: {samples}")
        train_merged[pn] = apply_override(baseline, pn, samples)

    train_dir = config.ARCHIVE_DIR / "v48_he_multi_sample"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v47_h = load_v47_holdout()
    HOLDOUT = [
        ("FFSH5065B", r"AA\FFSH5065B-F085-D.PDF"),
        ("FFSD1065B", r"AA\FFSD1065B-D.PDF"),
        ("VS3C20ET07T", r"AA\vs-3c20et07t-m3.pdf"),
        ("VS3C12ET07S2L", r"AA\vs-3c12et07s2l-m.pdf"),
        ("ASA006V065F4", r"AA\ASA006V065F4.pdf"),
    ]
    holdout_merged = {}
    for pn, rel in HOLDOUT:
        pdf_path = config.PROJECT_ROOT / rel
        baseline = {k: v for k, v in v47_h.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        if not needs_check(baseline):
            holdout_merged[pn] = baseline
            continue
        samples = query_he_n_times(backend, pn, pdf_path)
        print(f"  [{pn}] H_E samples: {samples}")
        holdout_merged[pn] = apply_override(baseline, pn, samples)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v48_he_multi_sample_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
