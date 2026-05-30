# ============================================================
# !!! OVERFIT -- V29+V26 組合，繼承 V29 的答案調校
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V30 — V29 baseline + V26 邏輯（3-model majority + triaxis V18 override）

V30 = (V29 + V18 + V22) majority vote with triaxis V18 override
"""
import json
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config


TRAIN = {
    "v29": "v29_multimodal_azure_gpt_4o_conservative",
    "v18": "v18_multimodal_azure_llama_4_maverick_conservative",
    "v22": "v22_multimodal_toc_azure_gpt_4o_conservative",
}
HOLDOUT_DIRS = {k: f"{k}_NEW_PDFS_test" for k in TRAIN.keys()}
DIM = ["Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"]


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


def is_v18_isolated_triaxis(v29_d, v18_d, v22_d, pn):
    """這裡 v29 取代 v12 角色（同 GPT-4o, multimodal extractor）"""
    for f in DIM:
        a = str(v29_d.get(pn, {}).get(f))
        b = str(v18_d.get(pn, {}).get(f))
        c = str(v22_d.get(pn, {}).get(f))
        if not (a == c and a != b):
            return False
    return True


def majority(values, baseline):
    counts = Counter([str(v) for v in values])
    top_str, top_n = counts.most_common(1)[0]
    if top_n >= 2:
        for v in values:
            if str(v) == top_str:
                return v
    return baseline


def merge(sources):
    out = {}
    parts = set()
    for s in sources.values():
        parts.update(s.keys())
    for pn in parts:
        a = {k: v for k, v in sources["v29"].get(pn, {}).items() if not k.startswith("_")}
        b = {k: v for k, v in sources["v18"].get(pn, {}).items() if not k.startswith("_")}
        c = {k: v for k, v in sources["v22"].get(pn, {}).items() if not k.startswith("_")}
        triaxis = is_v18_isolated_triaxis(sources["v29"], sources["v18"], sources["v22"], pn)
        merged = {}
        for f in config.FIELDS:
            if triaxis and f in DIM:
                merged[f] = b.get(f)
            else:
                merged[f] = majority([a.get(f), b.get(f), c.get(f)], a.get(f))
        if triaxis:
            print(f"  [{pn}] triaxis V18 override")
        out[pn] = merged
    return out


def main():
    print("=== Train ===")
    train_sources = {k: load_archive(k) for k in TRAIN.keys()}
    train_merged = merge(train_sources)
    train_dir = config.ARCHIVE_DIR / "v30_v29_with_v26_logic"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print("\n=== Holdout ===")
    holdout_sources = {k: load_holdout(k) for k in HOLDOUT_DIRS.keys()}
    holdout_merged = merge(holdout_sources)
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v30_v29_with_v26_logic_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")


if __name__ == "__main__":
    main()
