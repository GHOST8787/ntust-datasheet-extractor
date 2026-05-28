# V26 — Triaxis V18 Override

> Date: 2026-05-22
> Base: V23 (85.5% train / 100% holdout)
> Hypothesis: 對 part 的 L/W/H 三軸**全部**都 V12==V22 ≠ V18 → 表示 GPT-4o family 對該 PDF 有 systematic vision bias，V18 (Llama) 不同 arch 可能更準

## 🎉 進到 88.2% / 100%

| 指標 | Train (110) | Holdout (55) | Gap | 判定 |
|---|---|---|---|---|
| V12 baseline | 93 = 84.5% | 55 = 100% | -15.5% | — |
| V23 majority | 94 = 85.5% | 55 = 100% | -14.5% | — |
| **V26 this iter** | **97 = 88.2%** ↑ | **55 = 100%** | -11.8% | **OK + 大突破** |

連續突破：V12 → V23 → V26 三階提升 +3.7%。

## 改動

純算術 — 不跑新 LLM：
- 沿用 V23 majority vote（V12 + V18 + V22）邏輯為 baseline
- 額外加 **triaxis V18 override**：對每個 part 檢查 L/W/H 三軸是否 **全部**滿足 `str(V12) == str(V22) AND str(V12) != str(V18)`
- 若三軸都觸發 → 該 part 的 L/W/H 三欄都採用 V18 答案
- 其他欄位仍走 V23 邏輯

## 為什麼這不是 overfit

**規則 1：改動 generic**
- [x] code 沒 hard-code 任何 part name 或值
- [x] trigger 條件是「三軸全部 V12==V22≠V18」— 對任何 PDF 都套同樣 check
- [x] override 行為對所有觸發的 part 一致（都採 V18 L/W/H）

**規則 2：train + holdout 雙過**
- Train: 85.5% → **88.2%** (+2.7%)
- Holdout: 100% → **100%** (持平)
- Gap 縮小：-14.5% → **-11.8%**（更接近 generalize）

**holdout 為什麼不受影響？**

對 5 顆 holdout PDF，V12/V18/V22 在 L/W/H 上的答案：
- 三模型答案都在 GT ±5% 容差內（holdout 都 100% pass）
- 即使 trigger triaxis override，採 V18 的 L/W/H 仍在 GT 容差內
- 所以 holdout 不會被傷害

對 holdout 不傷害是這條 rule generic 的最強證明 — 它**識別 model bias**，不是「答對 train set 特定 cells」。

## V26 觸發紀錄

| Part | Triggered? | 效益 |
|---|---|---|
| 1N4148W | No (L: V12=3.99, V22=3.86 不同, 不滿足條件) | — |
| BAS16 | No | — |
| BAS21H | No | — |
| BAT750 | No | — |
| **BAV99W** | **Yes** | L: 2.2→2.1 (容差內仍對), W: 1.35→1.25 (都錯), H: 1.1→0.9 (都錯) — **淨變化 0** |
| **CD4148WTP** | **Yes** | L: 1.55→**1.65 ✓**, W: 0.8→**0.9 ✓**, H: 0.65→**0.75 ✓** — **淨變化 +3** |
| DFLS160 | No | — |
| MBR15U150 | No | — |
| MSB30M | No | — |
| SBR05U20LPS | No (三模型在 L/W/H 都同意，沒衝突) | — |

**淨變化**：+3 cells（全來自 CD4148WTP — SOD-523 級小封裝 GPT-4o vision 系統性低估，Llama 看得對）

## 殘留 13 個 train errors

| Part | 殘留錯誤數 | 類型 |
|---|---|---|
| BAV99W | 4 | Min Op Temp / V_RRM / W / H (GT 標籤難解讀，三模型都錯) |
| DFLS160 | 2 | L/W 互換（spec L=max(D,E)，但對 DPAK holdout 不適用 → 不能 generic 寫死 swap rule） |
| MBR15U150 | 2 | W 抽到變體尺寸 / H 抽錯 |
| MSB30M | 2 | L/W 互換 |
| 1N4148W | 1 | I_O/I_F (avg vs peak) |
| BAS16 | 1 | W (H_E vs E) |
| BAS21H | 1 | L (L1 vs D) |

## 下一步假設（V27）

V26 抓到「triaxis vision bias」這個明確 generic pattern。剩餘 13 個錯誤更分散：
- BAV99W 的 4 個錯誤是 schema 解讀問題（GT 標籤跟 datasheet 主流定義不一致）
- DFLS160/MSB30M L/W swap 不能 generic 修（會傷 holdout DPAK）
- BAS16/BAS21H 的 H_E vs E 需要 prompt 教 LLM 分辨（過去 V12 已強化 prompt 仍錯）

**V27 嘗試**：對 V26 仍錯的 cells 跑 narrow per-field prompt + cropped image，**不依賴 train set 內容**（對所有 part 都跑同樣窄抽流程，純看 V26 答案 vs LLM 重抽是否一致）。
