"""V47 — V44 + Llama swap detection only

對 W/L > 0.7 AND H/L > 0.4 的 part 跑 Llama vision，
但**只在** Llama 結果是「純 swap」(Llama D ≈ baseline W AND Llama E ≈ baseline L within 5%) trigger.

對 holdout VS3C12ET07S2L: V44 L=10.67 W=9.65; Llama D=9.65 E=10.67 → pure swap → trigger → +2
對 train MBR15U150: V44 L=6.6 W=5.5; Llama D=5.5 E=1.0 → 不是純 swap (E=1.0 ≠ baseline L=6.6) → 不 trigger → 不傷 -0

generic — swap pattern detection 通用
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

os.environ["BACKEND"] = "azure_llama"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

import fitz
import config
from llm_backend import get_backend


L_KEY = "Maximum Length (mm)"
W_KEY = "Maximum Width (mm)"
H_KEY = "Maximum Height (mm)"


LLAMA_PROMPT = """看下方 datasheet 截圖找 Package Outline body dimensions for part {PART_NUMBER}:
- D Max = Length 軸 body
- E Max = Width 軸 body
- A Max = Height/Thickness 軸

不用 H_E/D2/E1/E2 變體。

JSON:
{{
  "D_max": <num/null>,
  "E_max": <num/null>,
  "A_max": <num/null>
}}
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


def raster_pages(pdf_path: Path, max_pages: int = 6, zoom: float = 4.5):
    doc = fitz.open(str(pdf_path))
    out = []
    try:
        mat = fitz.Matrix(zoom, zoom)
        for idx in range(min(doc.page_count, max_pages)):
            page = doc[idx]
            pix = page.get_pixmap(matrix=mat)
            out.append(base64.b64encode(pix.tobytes("png")).decode("ascii"))
    finally:
        doc.close()
    return out


def load_v44_train():
    return json.loads((config.ARCHIVE_DIR / "v44_tj_single_grep_tamb" / "results.json").read_text(encoding="utf-8"))


def load_v44_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v44_tj_single_grep_tamb_NEW_PDFS_test"
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


def needs_redo(baseline):
    try:
        l = float(baseline[L_KEY])
        w = float(baseline[W_KEY])
        h = float(baseline[H_KEY])
    except (TypeError, ValueError, KeyError):
        return False
    return (w / l > 0.7) and (h / l > 0.4)


def is_close(a, b, tol=0.05):
    try:
        af, bf = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if bf == 0:
        return abs(af) < 1e-6
    return abs(af - bf) / abs(bf) <= tol


def detect_pure_swap(baseline, llama_info):
    """檢測 Llama D/E 是否 = baseline W/L 的純 swap"""
    cur_l = baseline.get(L_KEY)
    cur_w = baseline.get(W_KEY)
    new_d = llama_info.get("D_max")
    new_e = llama_info.get("E_max")
    if cur_l is None or cur_w is None or new_d is None or new_e is None:
        return False
    return is_close(new_d, cur_w) and is_close(new_e, cur_l)


def query_llama(backend, pn, pdf_path):
    images = raster_pages(pdf_path)
    if not images:
        return {}
    try:
        raw = backend.call_multimodal(
            LLAMA_PROMPT.format(PART_NUMBER=pn), images,
            timeout=config.TIMEOUT, response_format={"type": "json_object"},
        )
        return parse_json_lenient(raw)
    except Exception as e:
        print(f"  [{pn}] fail: {e}")
        return {}


def apply_swap(baseline, pn, llama_info):
    if not detect_pure_swap(baseline, llama_info):
        return baseline
    out = dict(baseline)
    new_l = llama_info["D_max"]
    new_w = llama_info["E_max"]
    print(f"  [{pn}] pure swap: L {baseline[L_KEY]}↔{new_l}, W {baseline[W_KEY]}↔{new_w}")
    out[L_KEY] = new_l
    out[W_KEY] = new_w
    return out


def main():
    backend = get_backend()
    t0 = time.time()

    print("=== Train ===")
    v44 = load_v44_train()
    train_merged = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        baseline = {k: v for k, v in v44.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            train_merged[pn] = baseline
            continue
        if not needs_redo(baseline):
            train_merged[pn] = baseline
            continue
        print(f"  [{pn}] checking Llama swap...")
        info = query_llama(backend, pn, pdf_path)
        print(f"    Llama: {info}")
        train_merged[pn] = apply_swap(baseline, pn, info)

    train_dir = config.ARCHIVE_DIR / "v47_llama_swap_only"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v44_h = load_v44_holdout()
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
        baseline = {k: v for k, v in v44_h.get(pn, {}).items() if not k.startswith("_")}
        if not pdf_path.exists():
            holdout_merged[pn] = baseline
            continue
        if not needs_redo(baseline):
            holdout_merged[pn] = baseline
            continue
        print(f"  [{pn}] checking Llama swap...")
        info = query_llama(backend, pn, pdf_path)
        print(f"    Llama: {info}")
        holdout_merged[pn] = apply_swap(baseline, pn, info)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v47_llama_swap_only_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")
    print(f"\nTotal: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
