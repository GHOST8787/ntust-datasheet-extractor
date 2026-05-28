"""對 5 顆新 PDF 用人工 ground truth 算 estimated 正確率

Ground truth 從 PDF Package Dimensions / Electrical Char 表手動抽出（2026-05-22）。
比對邏輯沿用 reevaluate.py 嚴格容差（numeric ±5% / text token ≥50%）。
"""
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, NUMERIC_TOLERANCE_LOOSE, TEXT_MATCH_THRESHOLD_LOOSE

# Ground truth 從 PDF Package Dimensions Max 欄 + Electrical Characteristics Max 欄 抽
GROUND_TRUTH = {
    "FFSH5065B": {  # TO-247-2LD
        "Part Number": "FFSH5065B",
        "Minimum Operating Temperature(°C)": -55,
        "Maximum Operating Temperature (°C)": 175,
        "Maximum Length (mm)": 20.82,
        "Maximum Width (mm)": 15.87,
        "Maximum Height (mm)": 4.82,
        "PIN Number": 2,
        "I_O、I_F (A)": 50,
        "V_F(Forward Voltage) (V)": "1.7 @50A,25°C、2.0 @50A,125°C、2.4 @50A,175°C",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
        "I_R(Reverse Current) ": "40uA @650V,25°C、80uA @650V,125°C、160uA @650V,175°C",
    },
    "FFSD1065B": {  # DPAK3
        "Part Number": "FFSD1065B",
        "Minimum Operating Temperature(°C)": -55,
        "Maximum Operating Temperature (°C)": 175,
        "Maximum Length (mm)": 6.22,   # D Max
        "Maximum Width (mm)": 6.73,    # E Max
        "Maximum Height (mm)": 2.39,   # A Max
        "PIN Number": 3,
        "I_O、I_F (A)": 10,
        "V_F(Forward Voltage) (V)": "1.7 @10A,25°C、2.0 @10A,125°C、2.4 @10A,175°C",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
        "I_R(Reverse Current) ": "40uA @650V,25°C、80uA @650V,125°C、160uA @650V,175°C",
    },
    "VS3C20ET07T": {  # TO-220AC 2L
        "Part Number": "VS3C20ET07T",
        "Minimum Operating Temperature(°C)": -55,
        "Maximum Operating Temperature (°C)": 175,
        "Maximum Length (mm)": 15.25,
        "Maximum Width (mm)": 10.51,
        "Maximum Height (mm)": 4.65,
        "PIN Number": 2,
        "I_O、I_F (A)": 20,
        # V_F Max 欄：25°C max=1.5, 150°C max=1.85, 175°C no Max（只給 typ）
        "V_F(Forward Voltage) (V)": "1.5 @20A,25°C、1.85 @20A,150°C",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
        # I_R Max 欄：25°C max=100, 150°C max=250, 175°C no Max
        "I_R(Reverse Current) ": "100uA @650V,25°C、250uA @650V,150°C",
    },
    "VS3C12ET07S2L": {  # D2PAK 2L
        "Part Number": "VS3C12ET07S2L",
        "Minimum Operating Temperature(°C)": -55,
        "Maximum Operating Temperature (°C)": 175,
        "Maximum Length (mm)": 9.65,
        "Maximum Width (mm)": 10.67,
        "Maximum Height (mm)": 4.83,
        "PIN Number": 2,
        "I_O、I_F (A)": 12,
        "V_F(Forward Voltage) (V)": "1.5 @12A,25°C、1.85 @12A,150°C",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
        "I_R(Reverse Current) ": "65uA @650V,25°C、150uA @650V,150°C",
    },
    "ASA006V065F4": {  # TO-252-2L
        "Part Number": "ASA006V065F4",
        "Minimum Operating Temperature(°C)": -55,
        "Maximum Operating Temperature (°C)": 175,
        "Maximum Length (mm)": 6.22,
        "Maximum Width (mm)": 6.73,
        "Maximum Height (mm)": 2.38,
        "PIN Number": 2,
        "I_O、I_F (A)": 19,
        "V_F(Forward Voltage) (V)": "1.45 @6A,25°C、1.70 @6A,175°C",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
        "I_R(Reverse Current) ": "48uA @650V,25°C、192uA @650V,175°C",
    },
}


def evaluate(extracted, gt, numeric_tol, text_threshold):
    out = {"overall": {"correct": 0, "total": 0}, "per_part": {}, "cells": []}
    for pn, exp_rec in gt.items():
        e = extracted.get(pn, {})
        pr = {"correct": 0, "total": 0, "fields": {}}
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
                pr["fields"][f] = {"expected": exp, "extracted": ext, "match": ok}
                pr["total"] += 1
                if ok:
                    pr["correct"] += 1
                out["cells"].append({"part": pn, "field": f, "expected": exp, "extracted": ext, "match": ok})
        pr["accuracy"] = pr["correct"] / pr["total"] if pr["total"] else 0
        out["per_part"][pn] = pr
        out["overall"]["correct"] += pr["correct"]
        out["overall"]["total"] += pr["total"]
    out["overall"]["accuracy"] = out["overall"]["correct"] / out["overall"]["total"]
    return out


def main():
    print("Ground truth: 5 parts × 11 fields = 55 cells")
    print()

    # 跑 V4 E baseline（原本 extract_new_pdfs.py 用 V4 E 配置跑的）
    paths = [
        ("V4 E (json_object, no V8)", config.OUTPUT_DIR / "new_pdfs_extracted.json"),
        # V8 跑完會寫到同個 path（被 V8_run 覆蓋）— 但 V8 archive 在 output/_archive/v8_*
        # 為了不互相覆蓋，V8 應該寫到自己的 path
    ]

    # V8 跑完後 archive 在 output/_archive/v8_multimodal_azure_gpt_4o_conservative/ 但 new pdfs 不歸檔
    # 改成讀 cell archive 內的 results.json 對 5 顆新 PDF：不在那 — 只在 new_pdfs_extracted.json
    # 暫時：先看 V4 E baseline；V8 跑完後再 manually 對

    for label, path in paths:
        if not path.exists():
            print(f"{label}: [MISSING] {path}")
            continue
        with open(path, encoding="utf-8") as f:
            extracted = json.load(f)

        strict = evaluate(extracted, GROUND_TRUTH, config.NUMERIC_TOLERANCE, config.TEXT_MATCH_THRESHOLD)
        loose = evaluate(extracted, GROUND_TRUTH, NUMERIC_TOLERANCE_LOOSE, TEXT_MATCH_THRESHOLD_LOOSE)

        print(f"=== {label} ===")
        print(f"  Strict (±5% / ≥50%): {strict['overall']['correct']}/{strict['overall']['total']} = {strict['overall']['accuracy']*100:.1f}%")
        print(f"  Loose  (±10%/ ≥30%): {loose['overall']['correct']}/{loose['overall']['total']} = {loose['overall']['accuracy']*100:.1f}%")
        print()
        print("  Per part:")
        for pn, pr in strict["per_part"].items():
            print(f"    {pn:<18} {pr['correct']:>3}/{pr['total']:>3} = {pr['accuracy']*100:>5.1f}%")
        print()
        print("  Errors (strict):")
        for c in strict["cells"]:
            if not c["match"]:
                exp_str = str(c["expected"])[:40]
                ext_str = str(c["extracted"])[:40]
                print(f"    [{c['part']:<18}] {c['field'][:38]:<38}  exp={exp_str!r:<42} ext={ext_str!r}")
        print()


if __name__ == "__main__":
    main()
