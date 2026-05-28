"""V25 — Cluster-aware majority vote

問題：V23 (3-model majority) 中，V12 跟 V22 都是 GPT-4o (同 model family)，
共同 outvote V18 (Llama family)。當 V18 真抽對而 GPT-4o family 同樣抽錯時，
naive majority 反而選錯。

解法：把 V12+V22 算 1 票（GPT-4o family vote），V18 算 1 票（Llama family vote）。
- 兩 family 同意 → 取共識
- 不同意 + V12==V22 (GPT-4o 內部同) → 仍平手，取 V18 (假設 Llama 多模態 cover GPT-4o blind spot)
- 不同意 + V12!=V22 (GPT-4o 內部分裂) → 取 V18 (因 GPT-4o 不確定)

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


TRAIN = {
    "v12": "v12_multimodal_azure_gpt_4o_conservative",
    "v18": "v18_multimodal_azure_llama_4_maverick_conservative",
    "v22": "v22_multimodal_toc_azure_gpt_4o_conservative",
}
HOLDOUT_DIRS = {k: f"{k}_NEW_PDFS_test" for k in TRAIN.keys()}


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


def cluster_vote(v12_val, v18_val, v22_val):
    """Cluster-aware vote:
    - GPT-4o family = (v12, v22); 若內部一致，當 1 票
    - Llama family = (v18); 1 票
    - 兩 family 同 → 共識
    - 不同 → 取 v18 (Llama family 通常被 outvote 但實際可能對)
    """
    s12, s18, s22 = str(v12_val), str(v18_val), str(v22_val)
    # GPT-4o 內部一致 → 算 1 票 "s12"
    if s12 == s22:
        gpt4o_vote = v12_val
        # 跟 Llama 比
        if s12 == s18:
            return v12_val
        else:
            # GPT-4o 同意 1.55 vs Llama 1.65 → 取 v18 (Llama 可能 cover blind spot)
            return v18_val
    else:
        # GPT-4o 內部分裂 (v12 ≠ v22) → Llama 票勝
        # 若 v18 跟 v12 或 v22 同 → 取那個
        if s18 == s12:
            return v12_val
        elif s18 == s22:
            return v22_val
        else:
            # 三個全不同 → 取 v18
            return v18_val


def merge(sources):
    out = {}
    parts = set()
    for s in sources.values():
        parts.update(s.keys())
    for pn in parts:
        a = {k: v for k, v in sources["v12"].get(pn, {}).items() if not k.startswith("_")}
        b = {k: v for k, v in sources["v18"].get(pn, {}).items() if not k.startswith("_")}
        c = {k: v for k, v in sources["v22"].get(pn, {}).items() if not k.startswith("_")}
        merged = {}
        for f in config.FIELDS:
            merged[f] = cluster_vote(a.get(f), b.get(f), c.get(f))
        out[pn] = merged
    return out


def main():
    train_sources = {k: load_archive(k) for k in TRAIN.keys()}
    train_merged = merge(train_sources)
    train_dir = config.ARCHIVE_DIR / "v25_cluster_aware_vote"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote train: {train_dir}")

    holdout_sources = {k: load_holdout(k) for k in HOLDOUT_DIRS.keys()}
    holdout_merged = merge(holdout_sources)
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v25_cluster_aware_vote_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote holdout: {log_dir}")


if __name__ == "__main__":
    main()
