# V22 — multimodal_toc PDF extractor

> Date: 2026-05-22
> Base: V12 (84.5% train / 100% holdout)
> Hypothesis: PDF TOC 結構定位機械頁比 V8 keyword grep 精準

## 改動

- `PDF_EXTRACTOR=multimodal_toc`（沿用既有 `MultiModalTocExtractor` class）
- 其他配置完全同 V12

## Overfit 證明

| 指標 | Train (110) | Holdout (55) | Gap | 判定 |
|---|---|---|---|---|
| V12 | 93 = 84.5% | 55 = 100% | -15.5% | — |
| V22 | **93 = 84.5%** | **55 = 100%** | -15.5% | **持平** |

不算 overfit 也不算改善（同分但錯不同 cell）。

## V12 vs V22 實際變化

| Part | Field | V12 | V22 | GT | 變化 |
|---|---|---|---|---|---|
| BAT750 | V_F | 0.28 @50mA...(對) | 0.235 @100mA...(錯) | 0.28 @50mA... | -1 |
| SBR05U20LPS | I_R | 6uA @20V...(錯) | 50uA @20V,25°C、5mA @20V,150°C(對) | 同 V22 | +1 |

**淨變化 = 0**。V22 PDF extractor 對某些 PDF 有改善（SBR05U20LPS），對某些有副作用（BAT750）。

## 啟示

V22 跟 V12 / V18 互補 — 各抽錯不同 cells。這是 V23 multi-model majority vote 的基礎。
