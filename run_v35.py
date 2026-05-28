"""V35 — 4-way vote (V12 + V18 + V22 + V29) with V26 triaxis V18 override

加 V29 進 V23 majority pool。V29 prompt 改了 Tj fallback 跟 I_O 優先。
若 V29 vs V12 在 IF / Min Op 不同 → 4-way majority 可能讓 V29 答案勝出（4 票中 V29 是新獨立觀察）

V26 triaxis override 仍套用。

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
    "v29": "v29_multimodal_azure_gpt_4o_conservative",
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


def is_v18_isolated_triaxis(sources, pn):
    """V12, V22, V29 都 == AND V18 不同（V12/V22/V29 都 GPT-4o family）"""
    for f in DIM:
        a = str(sources["v12"].get(pn, {}).get(f))
        b = str(sources["v18"].get(pn, {}).get(f))
        c = str(sources["v22"].get(pn, {}).get(f))
        d = str(sources["v29"].get(pn, {}).get(f))
        # 至少 2 個 GPT-4o family 同意 AND V18 不同
        gpt_same = (a == c == d) or (a == c and a != d) or (a == d and a != c) or (c == d and c != a)
        if not (gpt_same and a != b):
            return False
    return True


def majority_4(values, baseline):
    """4 票 majority: ≥2 同意取共識"""
    str_values = [str(v) for v in values]
    counts = Counter(str_values)
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
        a = {k: v for k, v in sources["v12"].get(pn, {}).items() if not k.startswith("_")}
        b = {k: v for k, v in sources["v18"].get(pn, {}).items() if not k.startswith("_")}
        c = {k: v for k, v in sources["v22"].get(pn, {}).items() if not k.startswith("_")}
        d = {k: v for k, v in sources["v29"].get(pn, {}).items() if not k.startswith("_")}
        triaxis = is_v18_isolated_triaxis(sources, pn)
        merged = {}
        for f in config.FIELDS:
            if triaxis and f in DIM:
                # V26 邏輯：採 V18
                merged[f] = b.get(f)
            else:
                # 4-way majority
                merged[f] = majority_4([a.get(f), b.get(f), c.get(f), d.get(f)], a.get(f))
        if triaxis:
            print(f"  [{pn}] triaxis V18 override")
        out[pn] = merged
    return out


def main():
    print("=== Train ===")
    train_sources = {k: load_archive(k) for k in TRAIN.keys()}
    train_merged = merge(train_sources)
    train_dir = config.ARCHIVE_DIR / "v35_4way_vote_with_v29"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print("\n=== Holdout ===")
    holdout_sources = {k: load_holdout(k) for k in HOLDOUT_DIRS.keys()}
    holdout_merged = merge(holdout_sources)
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v35_4way_vote_with_v29_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")


if __name__ == "__main__":
    main()
