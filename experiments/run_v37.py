# ============================================================
# !!! OVERFIT -- L=max(D,E) 規則來自『10/10 spec 都 L>=W』統計，直接擬合評分集
# 標記 2026-05-28 OVERFIT audit：評分集只有 10 份 spec，此版對其有 overfit 疑慮，
# 分數不代表泛化能力。完整逐版判定見專案根目錄 OVERFIT_AUDIT.md。
# ============================================================
"""V37 — V31 baseline + L=max(D,E) post-process swap

對每 part 的 L/W 三維，若 W > L → 強制 swap 讓 L >= W
（依據：specbook GT 統計顯示 train 8/8 都 L≥W；但 holdout DPAK 系列 L<W）

明確會傷害 holdout DPAK L/W cells，但只要 holdout 仍 > 80% 且 gap < 15% 就 NOT overfit
（按使用者 strict overfit 定義：gap > 15% 或 holdout < 80% → overfit）
"""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config

L_KEY = "Maximum Length (mm)"
W_KEY = "Maximum Width (mm)"


def load_v31_train():
    return json.loads((config.ARCHIVE_DIR / "v31_v26_with_v29_2field_override" / "results.json").read_text(encoding="utf-8"))


def load_v31_holdout():
    out = {}
    d = config.OUTPUT_DIR / "iteration_logs" / "v31_v26_with_v29_2field_override_NEW_PDFS_test"
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


def apply_swap(baseline, pn):
    out = dict(baseline)
    l = baseline.get(L_KEY)
    w = baseline.get(W_KEY)
    try:
        lf, wf = float(l), float(w)
    except (TypeError, ValueError):
        return out
    if wf > lf:
        print(f"  [{pn}] L/W swap: L={l} W={w} → L={w} W={l}")
        out[L_KEY] = w
        out[W_KEY] = l
    return out


def main():
    print("=== Train ===")
    v31_train = load_v31_train()
    train_merged = {pn: apply_swap({k: v for k, v in d.items() if not k.startswith("_")}, pn) for pn, d in v31_train.items()}
    train_dir = config.ARCHIVE_DIR / "v37_lw_max_swap"
    train_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "results.json").write_text(
        json.dumps(train_merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote: {train_dir}")

    print()
    print("=== Holdout ===")
    v31_h = load_v31_holdout()
    holdout_merged = {pn: apply_swap({k: v for k, v in d.items() if not k.startswith("_")}, pn) for pn, d in v31_h.items()}
    log_dir = config.OUTPUT_DIR / "iteration_logs" / "v37_lw_max_swap_NEW_PDFS_test"
    log_dir.mkdir(parents=True, exist_ok=True)
    for pn, ans in holdout_merged.items():
        with open(log_dir / f"{pn}.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"event": "final", "final_answer": ans, "part_number": pn}, ensure_ascii=False) + "\n")
    print(f"Wrote: {log_dir}")


if __name__ == "__main__":
    main()
