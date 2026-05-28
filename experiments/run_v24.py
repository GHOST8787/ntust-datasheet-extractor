"""V24 — 擴大 model 池到 8 個做 majority vote

8 個 sources（都是 84.5% / 81.8% train 等級）:
  V10 / V11 / V12 / V14 / V15 / V17 / V18 / V22

對每 (part, field)：
  - 取出 8 個答案
  - 找出出現次數 ≥4 的（過半）
  - 若沒有 ≥4，找 ≥3 的（多數但非過半）
  - 都沒則回退 V12 baseline

純算術 — 不跑新 LLM。
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


TRAIN_SOURCES = {
    "v10": "v10_multimodal_azure_gpt_4o_conservative",
    "v11": "v11_multimodal_azure_gpt_4o_conservative",
    "v12": "v12_multimodal_azure_gpt_4o_conservative",
    "v14": "v14_multimodal_azure_gpt_4o_conservative",
    "v15": "v15_multimodal_azure_gpt_4o_strict",
    "v17": "v17_multimodal_azure_gpt_4o_conservative",
    "v18": "v18_multimodal_azure_llama_4_maverick_conservative",
    "v22": "v22_multimodal_toc_azure_gpt_4o_conservative",
}

HOLDOUT_LOGDIRS = {k: f"{k}_NEW_PDFS_test" for k in TRAIN_SOURCES.keys()}


def load_archive_train(name: str) -> dict:
    p = config.ARCHIVE_DIR / TRAIN_SOURCES[name] / "results.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_holdout_logs(logdir_key: str) -> dict:
    d = config.OUTPUT_DIR / "iteration_logs" / HOLDOUT_LOGDIRS[logdir_key]
    out = {}
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


def majority_vote_n(values, baseline_value, threshold_ratio=0.5):
    """N 個值的 majority：≥threshold_ratio 同意取共識
    支援 None / 物件值
    """
    str_values = [str(v) for v in values]
    counts = Counter(str_values)
    n = len(values)
    most_common_str, most_common_n = counts.most_common(1)[0]
    if most_common_n / n >= threshold_ratio:
        # 回原始非字串化值
        for v in values:
            if str(v) == most_common_str:
                return v
    return baseline_value


def merge(sources: dict, baseline_key: str = "v12") -> dict:
    out = {}
    baseline = sources[baseline_key]
    parts = set()
    for src in sources.values():
        parts.update(src.keys())
    for pn in parts:
        recs = []
        for k, src in sources.items():
            r = src.get(pn, {})
            r = {k2: v for k2, v in r.items() if not k2.startswith("_")}
            recs.append(r)
        base = baseline.get(pn, {})
        base = {k: v for k, v in base.items() if not k.startswith("_")}
        merged = {}
        for f in config.FIELDS:
            values = [r.get(f) for r in recs]
            merged[f] = majority_vote_n(values, base.get(f), threshold_ratio=0.5)
        out[pn] = merged
    return out


def main():
    # Train
    train_sources = {k: load_archive_train(k) for k in TRAIN_SOURCES.keys()}
    print(f"Train sources loaded: {list(train_sources.keys())}")
    train_merged = merge(train_sources)

    train_dir = config.ARCHIVE_DIR / "v24_majority_vote_8model"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote train: {train_dir}")

    # Holdout
    holdout_sources = {k: load_holdout_logs(k) for k in HOLDOUT_LOGDIRS.keys()}
    print(f"Holdout sources loaded: { {k: len(v) for k, v in holdout_sources.items()} }")
    holdout_merged = merge(holdout_sources)

    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v24_majority_vote_8model_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote holdout: {log_dir}")


if __name__ == "__main__":
    main()
