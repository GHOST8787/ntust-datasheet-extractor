# V{N} — {標題}

> Date: YYYY-MM-DD
> Base version: V{N-1}
> Hypothesis: 一句話描述為什麼這個改動會有效

## 改動內容

generic 改動的具體描述（不能是 per-part hack）：
- 改 `<檔名>:<行號>` ...

## 為什麼這不是 overfit（強制證明）

**規則 1：改動必須是 generic — 不依賴 train set 的特定元件名稱、特定 PDF 名稱、特定錯誤值**

- [ ] 我的 prompt / code 沒寫 `BAV99W` / `DFLS160` / `MSB30M` 等 train set 元件名稱
- [ ] 我的 prompt / code 沒寫 train set 內的具體錯誤數值（如 "2.2" "1.93" 等）
- [ ] 改動是針對「抽取機制」而非「答案表」

**規則 2：必須同時在 train + holdout 不退步**

| 指標 | Train (8 cells × 11) | Holdout (5 cells × 11) | Gap | 判定 |
|---|---|---|---|---|
| V{N-1} baseline | XX/88 = XX.X% | XX/55 = XX.X% | XX.X% | — |
| V{N} this iter | XX/88 = XX.X% | XX/55 = XX.X% | XX.X% | OK / OVERFIT |

**Overfit 判定：**
- 若 gap (train − holdout) > 15% → OVERFIT
- 若 holdout < V4 E baseline (80%) → OVERFIT
- 若 train ↑ 但 holdout ↓ > 5% → OVERFIT（直接傷害 generalization）

## Train errors 分佈（V{N}）

| Part | Field | Expected | Extracted | 錯誤類型 |
|---|---|---|---|---|

## Holdout errors 分佈（V{N}）

| Part | Field | Expected | Extracted | 錯誤類型 |
|---|---|---|---|---|

## 下一步假設（V{N+1}）

