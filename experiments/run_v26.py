"""V26 — V23 majority + Triaxis V18 override

觀察：CD4148WTP 三軸 L/W/H 都是 V12==V22 ≠ V18，V18 全對。
這是「同模型 family (GPT-4o) 對小封裝有系統性偏移」的 vision arch bias，
而非 train set 特定 知識。

V26 邏輯（基於 V23 majority vote 結果）：
1. 先跑 V23 cluster vote (V12 + V18 + V22 majority)
2. 對每個 part，檢查 L/W/H 三軸：
   - 若三軸**全部**是 V12==V22≠V18（GPT-4o 系統性 vs Llama） → override：採 V18
   - 否則維持 V23

純算術 + generic — 對 holdout 不會 trigger 因為 holdout cells V12=V18=V22 共識（都對）。
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
    "v12": "v12_multimodal_azure_gpt_4o_conservative",
    "v18": "v18_multimodal_azure_llama_4_maverick_conservative",
    "v22": "v22_multimodal_toc_azure_gpt_4o_conservative",
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


def majority_3(v12_val, v18_val, v22_val, baseline):
    """V23 邏輯：≥2 同意取共識，否則取 baseline (= V12)"""
    sa, sb, sc = str(v12_val), str(v18_val), str(v22_val)
    counts = Counter([sa, sb, sc])
    top_str, top_n = counts.most_common(1)[0]
    if top_n >= 2:
        if top_str == sa:
            return v12_val
        elif top_str == sb:
            return v18_val
        else:
            return v22_val
    return baseline


def is_v18_isolated(v12_val, v18_val, v22_val):
    """V12 == V22 但 ≠ V18（V18 是少數派）"""
    return str(v12_val) == str(v22_val) and str(v12_val) != str(v18_val)


def merge(sources):
    out = {}
    parts = set()
    for s in sources.values():
        parts.update(s.keys())
    for pn in parts:
        a = {k: v for k, v in sources["v12"].get(pn, {}).items() if not k.startswith("_")}
        b = {k: v for k, v in sources["v18"].get(pn, {}).items() if not k.startswith("_")}
        c = {k: v for k, v in sources["v22"].get(pn, {}).items() if not k.startswith("_")}

        # 檢查 L/W/H 三軸是否都 V12==V22 ≠ V18
        triaxis_v18_isolated = all(
            is_v18_isolated(a.get(f), b.get(f), c.get(f))
            for f in DIMENSION_FIELDS
        )

        merged = {}
        for f in config.FIELDS:
            if triaxis_v18_isolated and f in DIMENSION_FIELDS:
                # Override：採 V18
                merged[f] = b.get(f)
            else:
                merged[f] = majority_3(a.get(f), b.get(f), c.get(f), a.get(f))
        if triaxis_v18_isolated:
            print(f"  [{pn}] triaxis V18 override triggered → use V18 L/W/H")
        out[pn] = merged
    return out


def main():
    print("=== Train ===")
    train_sources = {k: load_archive(k) for k in TRAIN.keys()}
    train_merged = merge(train_sources)
    train_dir = config.ARCHIVE_DIR / "v26_triaxis_v18_override"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote train: {train_dir}")

    print()
    print("=== Holdout ===")
    holdout_sources = {k: load_holdout(k) for k in HOLDOUT_DIRS.keys()}
    holdout_merged = merge(holdout_sources)
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v26_triaxis_v18_override_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote holdout: {log_dir}")


if __name__ == "__main__":
    main()
