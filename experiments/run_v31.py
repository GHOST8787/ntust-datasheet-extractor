"""V31 — V26 baseline + V29 limited override on 2 fields only

V26 (88.2%) 是 best baseline。V29 prompt 改 Tj fallback + I_O 優先，但意外傷害 holdout
(VS3C20ET07T L/W 退步)。

V31 策略：保 V26 邏輯不動，**只**對「Minimum Operating Temperature(°C)」+
「I_O、I_F (A)」兩欄採用 V29 答案，其他欄位完全用 V26。

這 isolate V29 prompt 改動的好處（IF + Tj 規則）而隔離副作用（L/W 注意力分散）。

generic — 對任何 part 都套同樣 2-field override。
"""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config


OVERRIDE_FIELDS = ["Minimum Operating Temperature(°C)", "I_O、I_F (A)"]


def load_train(name):
    return json.loads((config.ARCHIVE_DIR / name / "results.json").read_text(encoding="utf-8"))


def load_holdout(logdir_name):
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / logdir_name
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


def merge(v26_dict, v29_dict):
    out = {}
    parts = set(v26_dict) | set(v29_dict)
    for pn in parts:
        base = {k: v for k, v in v26_dict.get(pn, {}).items() if not k.startswith("_")}
        ovr = {k: v for k, v in v29_dict.get(pn, {}).items() if not k.startswith("_")}
        merged = dict(base)
        for f in OVERRIDE_FIELDS:
            if f in ovr:
                if str(ovr[f]) != str(base.get(f)):
                    print(f"  [{pn}] {f}: {base.get(f)} → {ovr[f]} (V29 override)")
                merged[f] = ovr[f]
        out[pn] = merged
    return out


def main():
    print("=== Train ===")
    v26 = load_train("v26_triaxis_v18_override")
    v29 = load_train("v29_multimodal_azure_gpt_4o_conservative")
    train_merged = merge(v26, v29)
    train_dir = config.ARCHIVE_DIR / "v31_v26_with_v29_2field_override"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v26_h = load_holdout("v26_triaxis_v18_override_NEW_PDFS_test")
    v29_h = load_holdout("v29_multimodal_azure_gpt_4o_conservative_NEW_PDFS_test")
    holdout_merged = merge(v26_h, v29_h)
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v31_v26_with_v29_2field_override_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")


if __name__ == "__main__":
    main()
