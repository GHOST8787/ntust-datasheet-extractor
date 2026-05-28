"""V23 — V12 + V18 + V22 三模型 simple majority vote per cell

不重跑 LLM。對每 cell：
- 3 個都同意 → 取共識（已對）
- 2 個同意 → 取多數
- 3 個都不同 → 取 V12（baseline）

V12 = GPT-4o + V8 extractor (keyword grep)
V18 = Llama-4-Maverick + V8 extractor
V22 = GPT-4o + TOC extractor

三個維度 variation：(model, extractor, prompt)
"""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config


SOURCES_TRAIN = {
    "v12": config.ARCHIVE_DIR / "v12_multimodal_azure_gpt_4o_conservative" / "results.json",
    "v18": config.ARCHIVE_DIR / "v18_multimodal_azure_llama_4_maverick_conservative" / "results.json",
    "v22": config.ARCHIVE_DIR / "v22_multimodal_toc_azure_gpt_4o_conservative" / "results.json",
}

SOURCES_HOLDOUT_LOGDIRS = {
    "v12": "v12_NEW_PDFS_test",
    "v18": "v18_NEW_PDFS_test",
    "v22": "v22_NEW_PDFS_test",
}


def load_archive(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def load_holdout_from_logs(logdir_name: str) -> dict:
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / logdir_name
    if not d.exists():
        return out
    for jsonl_path in d.glob("*.jsonl"):
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


def majority_vote(values, baseline_value):
    """3 個值的多數決：≥2 同意取共識，否則取 baseline"""
    counts = {}
    for v in values:
        key = str(v)
        counts[key] = counts.get(key, 0) + 1
    # 找出 ≥2 票的
    for k, c in counts.items():
        if c >= 2:
            # 回傳該 key 對應的原始值（不是字串化的）
            for v in values:
                if str(v) == k:
                    return v
    return baseline_value


def merge_majority(v12: dict, v18: dict, v22: dict) -> dict:
    out = {}
    parts = set(v12) | set(v18) | set(v22)
    for pn in parts:
        a = v12.get(pn, {})
        b = v18.get(pn, {})
        c = v22.get(pn, {})
        # strip _v3_history / _history / _reasoning
        a = {k: v for k, v in a.items() if not k.startswith("_")}
        b = {k: v for k, v in b.items() if not k.startswith("_")}
        c = {k: v for k, v in c.items() if not k.startswith("_")}
        merged = {}
        for f in config.FIELDS:
            merged[f] = majority_vote([a.get(f), b.get(f), c.get(f)], a.get(f))
        out[pn] = merged
    return out


def main():
    # Train
    v12_train = load_archive(SOURCES_TRAIN["v12"])
    v18_train = load_archive(SOURCES_TRAIN["v18"])
    v22_train = load_archive(SOURCES_TRAIN["v22"])
    train_merged = merge_majority(v12_train, v18_train, v22_train)

    train_dir = config.ARCHIVE_DIR / "v23_majority_vote_3model"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote train: {train_dir / 'results.json'}")

    # Holdout
    v12_h = load_holdout_from_logs(SOURCES_HOLDOUT_LOGDIRS["v12"])
    v18_h = load_holdout_from_logs(SOURCES_HOLDOUT_LOGDIRS["v18"])
    v22_h = load_holdout_from_logs(SOURCES_HOLDOUT_LOGDIRS["v22"])
    print(f"Holdout sources loaded: v12={len(v12_h)}, v18={len(v18_h)}, v22={len(v22_h)}")
    holdout_merged = merge_majority(v12_h, v18_h, v22_h)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v23_majority_vote_3model_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote holdout logs to: {log_dir}")


if __name__ == "__main__":
    main()
