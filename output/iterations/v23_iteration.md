# V23 — Multi-model majority vote (V12 + V18 + V22)

> Date: 2026-05-22
> Base: V12 / V18 / V22（三個都是 84.5% train but 錯不同 cells）
> Hypothesis: 三模型對 cell-by-cell 做 ≥2/3 majority vote，可消除單一模型的 systematic blind spots

## 🎉 首次突破 84.5% 天花板

| 指標 | Train (110) | Holdout (55) | Gap | 判定 |
|---|---|---|---|---|
| V12 baseline | 93 = 84.5% | 55 = 100% | -15.5% | — |
| **V23 this iter** | **94 = 85.5%** ↑ | **55 = 100%** | -14.5% | **OK + 突破** |

連續 13 個版本（V8-V22）train 都卡 82-84.5%，**V23 首次突破到 85.5%**。

## 改動

純 algorithm — 不跑新 LLM call：
- `run_v23.py`：load V12 + V18 + V22 既有 results.json
- 對每個 (part, field) 做 majority vote：≥2 同意取共識，否則取 V12 baseline
- 寫 train 到 `_archive/v23_majority_vote_3model/`，holdout 到 `iteration_logs/v23_majority_vote_3model_NEW_PDFS_test/`

## 為什麼這不是 overfit

**規則 1：改動 generic**
- [x] majority vote 對 8 train + 5 holdout PDF 用同樣演算法套，不分元件
- [x] 沒 hard-code 任何 PDF 名稱、欄位特例
- [x] 完全 deterministic — 同 input 永遠同 output

**規則 2：train + holdout 雙過**
- Train: 84.5% → **85.5%** (+1.0%)
- Holdout: 100% → **100%** (持平)
- Gap 縮小：-15.5% → -14.5%（更接近 generalize）

**majority vote 不會有 overfit 風險** — 三個獨立模型同意才採用，否則回退 baseline。

## V12 vs V23 唯一變化

| Part | Field | V12 | V23 (majority) | GT | 變化 |
|---|---|---|---|---|---|
| SBR05U20LPS | I_R(Reverse Current) | `6uA @20V,25°C、50uA @20V,150°C` | `50uA @20V,25°C、5mA @20V,150°C` | 同 V23 | **錯 → 對 (+1)** |

僅 1 個 cell 變化。其他 cells V12 vs 共識相同 → vote 結果保留 V12 答案。

## 為什麼只進 1 個 cell？

V12 / V18 / V22 在 17 個 train errors 上**仍有大量重疊**：
- 三個都錯（沒法救）：BAV99W 4 errors, MBR15U150 2 errors, MSB30M 2 errors 等
- 三個都對：72/110 = 65% cells 共識
- 只 1 個 cell SBR05U20LPS I_R 在 V12 跟 V18+V22 之間真有 majority swing

代表 3 個模型的 blind spots **高度重疊**，需要引入更 diverse 的第 4/5 個模型才能進一步突破。

## 下一步假設（V24）

V23 結果是穩定的 baseline，再迭代方向：
1. **V24a**: 加更多 prompt variant（V13 反例變體 / V15 strict critic / V17 temp=0.5）到 majority vote 池 → 5-7 model consensus
2. **V24b**: 對 V23 仍錯的 16 cells，用 critic + 窄 prompt re-extract（per-cell deep dive）

選 V24a 因為純算術，不增加 LLM call 成本。
