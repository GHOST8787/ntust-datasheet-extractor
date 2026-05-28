# Baseline 統整 — V2 到 V19 全版本對照

> Date: 2026-05-22
> 從 `output/baseline_table.md` + `_archive/*/errors_detail.json` 統整

## 整體分數表

| Version | Train (110 cells) | Holdout (55 cells) | Gap | 備註 |
|---|---|---|---|---|
| V2 GPT-4o | 76.4% | — | — | pdfplumber baseline |
| V2 Mistral | 76.4% | — | — | |
| V4 E GPT-4o MM | 79.1% | — | — | multimodal 首次 |
| V8 | 82.7% | 80.0% | +2.7% | 三層 keyword 排序 |
| V9 | 83.6% | 89.1% | -5.5% | |
| V10/V11 | 84.5% | 94.5% | -10.0% | |
| **V12** | **84.5%** | **100%** | -15.5% | in-context 範例 |
| V13 | 81.8% | 96.4% | -14.5% | 反例 5-8 加入 → 退步 |
| **V14** | **84.5%** | **100%** | -15.5% | MM critic |
| **V15** | **84.5%** | **100%** | -15.5% | strict critic |
| V16 | 81.8% | 100% | -18.2% | hybrid critic 沒改善 |
| V17 | 84.5% | 98.2% | -13.6% | temp=0.5 |
| **V18** | **84.5%** | **100%** | -15.5% | Llama-4-Maverick |
| V19 | 83.6% | — | — | ensemble (退步) |

## Best 群 (84.5% train / 100% holdout)

**V10 / V11 / V12 / V14 / V15 / V17 / V18** 都打到 84.5% 卡死。換 prompt、換模型、換 critic 模式都沒突破。

## V12 baseline 17 個 train errors 結構分析

| 錯誤類型 | 個數 | 占比 | 元件 |
|---|---|---|---|
| 機械尺寸 L/W/H | 13 | 76% | BAS16, BAS21H, BAV99W, CD4148WTP, DFLS160, MBR15U150, MSB30M |
| Min Op Temp | 1 | 6% | BAV99W (GT=150 vs 抽=-55) |
| V_RRM | 1 | 6% | BAV99W (GT=150 vs 抽=100) |
| I_O / I_F | 1 | 6% | 1N4148W (GT=0.15 vs 抽=0.3) |
| I_R | 1 | 6% | SBR05U20LPS (溫度條件少一條) |

## 機械尺寸 13 個錯誤再細分

| 模式 | 個數 | 案例 |
|---|---|---|
| L/W 互換 | 4 | DFLS160 (3.9↔1.93), MSB30M (8.6↔6.7) |
| 抽到 footprint 不是 package | 3 | BAS16, BAS21H, BAV99W W |
| 小封裝精度差 | 3 | CD4148WTP L=1.55/0.8/0.65 vs GT=1.65/0.9/0.75 |
| 抽錯到變體尺寸 | 3 | MBR15U150 W=5.5, H=4.1 / BAV99W H |

## 卡關原因

V12-V18 的 prompt 已經包含：
- D/E/A vs JEDEC 對應規則
- Package Outline vs Footprint 區分
- MAX 欄取值
- in-context 範例（TO-247 / DPAK / D2PAK）
- 反例（4 條常見錯）
- multimodal critic 也看圖

仍卡 84.5%。代表純 prompt engineering 路線已**邊際效益歸零**。

## V20+ 方向

從 best (V12-V18) 都打 84.5% 但錯不同 cells 看：**V12 跟 V18 各對 13/17 不同錯**。
這暗示有「per-PDF 視覺 ambiguity」— 同樣的 prompt 看到同樣的圖，不同模型抽出不同結果。

**V20 假設**：增加 PDF 截圖品質（zoom 從 3.5 → 4.5）+ 截圖優先送 Package Outline 頁。
generic 改進，不依賴 train set 內容。
