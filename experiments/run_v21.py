"""V21 — Crop-based deep dive on L/W/H cells

Load V12 baseline answer → 對 L/W/H 三個機械尺寸用 crop_extractor 抓 Package Outline
區塊 → 帶 cropped 圖 + 窄 prompt 重抽 L/W/H → 替換 V12 answer。

純 generic 流程 — 不依賴 train set 元件名。
"""
import json
import os
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
from validators import validate_and_fix


V12_TRAIN_ARCHIVE = "v12_multimodal_azure_gpt_4o_conservative"
V12_HOLDOUT_LOGDIR = "v12_NEW_PDFS_test"  # iteration_logs/<this>/<part>.jsonl event=final


NARROW_DIMENSION_PROMPT = """你是專業電子元件 datasheet 機械尺寸抽取專家。

下方提供一張**裁剪過的 Package Outline / Mechanical Drawing 區塊圖**（已 crop 到包含尺寸表格 + 圖示的範圍）。

# 任務
從圖中抽出指定型號的 **Body Dimensions Max 值**：
- **Maximum Length (mm)** = D Max（JEDEC body D 軸尺寸 Max 欄）
- **Maximum Width (mm)**  = E Max（JEDEC body E 軸尺寸 Max 欄）
- **Maximum Height (mm)** = A Max（JEDEC body A 軸尺寸 Max 欄）

# 指定型號
Part Number: {PART_NUMBER}

# 關鍵規則

1. **永遠取 MAX 欄**（不是 NOM / TYP / MIN）
2. **D → Length / E → Width / A → Height**（硬性對應，**不論物理上哪個比較長**）
3. **禁止用 D2 / E1 / E2 / H_E / L / L1** 等變體當 L/W/H — 變體是引腳長度 / 散熱片 / 含引腳跨距，不是 body
4. **單位 mm**；若表頭是 inches，每值 × 25.4
5. **若圖中包含 Recommended Land Pattern / Footprint 圖**，**禁止取那張的數值** — body 尺寸只能來自 Package Outline / Mechanical Drawing 那張表
6. 若 image 太模糊看不清 Max 欄，回 `null`，不要猜

# 輸出 JSON

```json
{{
  "Maximum Length (mm)": <D Max 浮點 或 null>,
  "Maximum Width (mm)": <E Max 浮點 或 null>,
  "Maximum Height (mm)": <A Max 浮點 或 null>,
  "_reasoning": "簡述：D Max=? / E Max=? / A Max=? 的依據（表內第幾列、哪一欄）"
}}
```

只輸出 JSON，前後不要文字。
"""


def load_v12_baseline_train():
    """從 V12 archive 拿 train results"""
    p = config.ARCHIVE_DIR / V12_TRAIN_ARCHIVE / "results.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_v12_baseline_holdout():
    """從 iteration_logs V12_NEW_PDFS_test 還原 holdout final answer"""
    log_dir = config.OUTPUT_DIR / "iteration_logs" / V12_HOLDOUT_LOGDIR
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


def parse_json_lenient(text: str):
    """容錯 json parse — strip code fence + 找 {...}"""
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


def redo_dimensions(backend, pn: str, pdf_path: Path, baseline: dict) -> dict:
    """對單一元件用 crop + 窄 prompt 重抽 L/W/H，更新 baseline 並回傳"""
    crops = get_dimension_crops(pdf_path, zoom=5.0, max_crops=3)
    if not crops:
        print(f"    [{pn}] no dimension crops found, keep V12 baseline", flush=True)
        return baseline

    images_b64 = [b64 for (_, b64) in crops]
    pages = [p for (p, _) in crops]
    print(f"    [{pn}] {len(crops)} crops from pages {pages}", flush=True)

    prompt = NARROW_DIMENSION_PROMPT.format(PART_NUMBER=pn)
    try:
        raw = backend.call_multimodal(
            prompt, images_b64,
            timeout=config.TIMEOUT,
            response_format={"type": "json_object"},
        )
        parsed = parse_json_lenient(raw)
    except Exception as e:
        print(f"    [{pn}] redo fail: {e}, keep V12", flush=True)
        return baseline

    # 合併：只更新 L/W/H，其他保持 V12
    updated = dict(baseline)
    for f in ("Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"):
        if f in parsed and parsed[f] is not None:
            old_val = baseline.get(f)
            new_val = parsed[f]
            if str(old_val) != str(new_val):
                print(f"      {f}: {old_val} → {new_val}", flush=True)
            updated[f] = new_val

    # 過本地 validator 一次（修明顯範圍錯）
    updated, fixes = validate_and_fix(updated, pn)
    for fix in fixes:
        print(f"      [validator] {fix}", flush=True)

    return updated


def main():
    backend = get_backend()
    overall_t0 = time.time()

    # ===== Train =====
    print("=" * 80)
    print("V21 — Crop-based redo on TRAIN (8 specbook parts)")
    print("=" * 80)
    train_baseline = load_v12_baseline_train()
    train_redone = {}
    for pn, pdf_fn in config.PART_TO_PDF.items():
        pdf_path = config.DATASHEETS_DIR / pdf_fn
        if not pdf_path.exists():
            print(f"  [{pn}] PDF missing, skip")
            train_redone[pn] = train_baseline.get(pn, {})
            continue
        print(f"  - {pn}")
        baseline = train_baseline.get(pn, {})
        # strip _v3_history
        clean_baseline = {k: v for k, v in baseline.items() if not k.startswith("_")}
        train_redone[pn] = redo_dimensions(backend, pn, pdf_path, clean_baseline)

    # 寫 train results
    train_dir = config.ARCHIVE_DIR / "v21_crop_dimension_redo"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_redone, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote: {train_dir / 'results.json'}")

    # ===== Holdout =====
    print()
    print("=" * 80)
    print("V21 — Crop-based redo on HOLDOUT (5 new PDFs)")
    print("=" * 80)
    holdout_baseline = load_v12_baseline_holdout()

    HOLDOUT_PDFS = [
        ("FFSH5065B",     r"AA\FFSH5065B-F085-D.PDF"),
        ("FFSD1065B",     r"AA\FFSD1065B-D.PDF"),
        ("VS3C20ET07T",   r"AA\vs-3c20et07t-m3.pdf"),
        ("VS3C12ET07S2L", r"AA\vs-3c12et07s2l-m.pdf"),
        ("ASA006V065F4",  r"AA\ASA006V065F4.pdf"),
    ]

    holdout_redone = {}
    for pn, rel in HOLDOUT_PDFS:
        pdf_path = config.PROJECT_ROOT / rel
        if not pdf_path.exists():
            print(f"  [{pn}] PDF missing at {pdf_path}, skip")
            holdout_redone[pn] = holdout_baseline.get(pn, {})
            continue
        print(f"  - {pn}")
        baseline = holdout_baseline.get(pn, {})
        clean_baseline = {k: v for k, v in baseline.items() if not k.startswith("_")}
        holdout_redone[pn] = redo_dimensions(backend, pn, pdf_path, clean_baseline)

    holdout_log_dir = config.OUTPUT_DIR / "iteration_logs" / "v21_crop_dimension_redo_NEW_PDFS_test"
    holdout_log_dir.mkdir(parents=True, exist_ok=True)
    # 寫 jsonl 樣式（每 part 一個 jsonl 含 event=final），保證 evaluate_all 能讀
    for pn, ans in holdout_redone.items():
        with open(holdout_log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")

    print()
    print(f"Total: {time.time() - overall_t0:.1f}s")
    print()
    print("Next: python evaluate_all.py to compare train/holdout vs V12 baseline")


if __name__ == "__main__":
    main()
