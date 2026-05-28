# V21 — Crop-based deep dive on L/W/H cells

> Date: 2026-05-22
> Base version: V12
> Hypothesis: 用 `page.search_for("Package Outline")` 找 anchor bbox，crop 該區塊高 zoom (5x) 給 LLM，搭配「只問 L/W/H」窄 prompt，能消除 footprint vs body 混淆

## 改動內容

純 generic — 不依賴 train set 內容：
- 新檔 `crop_extractor.py`：PyMuPDF `page.search_for(keyword)` 找 anchor bbox → 擴展 (up 50, down 400, left 50, right 500) point → 5x zoom crop PNG
- 新檔 `run_v21.py`：
  - load V12 archive train results + V12 NEW_PDFS_test final answers
  - 對每個元件用 `get_dimension_crops()` 抓 dimension 區塊圖
  - 帶 cropped 圖 + 「只問 D Max / E Max / A Max」窄 prompt 給 GPT-4o multimodal 重抽
  - 只覆蓋 L/W/H 三欄，其他保持 V12

## 為什麼這不是 overfit

**規則 1：改動 generic**
- [x] code 沒寫 train set 元件名（流程套所有 PDF）
- [x] anchor keywords 是業界 datasheet 通用詞（"Package Outline" 等）
- [x] prompt 是 D/E/A → L/W/H 通用對應

**規則 2：train + holdout 數字**

| 指標 | Train (110) | Holdout (55) | Gap | 判定 |
|---|---|---|---|---|
| V12 baseline | 93 = 84.5% | 55 = 100% | -15.5% | — |
| V21 this iter | **93 = 84.5%** | **55 = 100%** | -15.5% | **持平 — neutral** |

不算 overfit（兩端都沒退步）也不算改善。

## V21 實際 cell 變化（train）

對 8 顆 train PDF：
- 5 顆找到 anchor 跑了 crop redo（1N4148W / BAS16 / BAV99W / MSB30M / SBR05U20LPS）
- 2 顆 anchor 沒找到（CD4148WTP / MBR15U150）keep V12 baseline

L/W/H 值變化：
| Part | Field | V12 → V21 | GT | 變化 |
|---|---|---|---|---|
| 1N4148W | L | 3.99 → 3.86 | 3.99 | 仍對（3.3% 內） |
| 1N4148W | W | 1.85 → 2.84 | 1.85 | **對 → 錯** |
| BAS16 | W | 1.4 → 2.5 | 2.5 | **錯 → 對** |
| BAV99W | H | 1.1 → 0.9 | 1.0 | 都錯（差 10%） |
| MSB30M | W | 7.4 → 8.6 | 6.7 | 都錯 |

淨變化：+1 (BAS16) − 1 (1N4148W W) = 0

## 為什麼沒淨進步

1. **anchor 找不到的 PDF (CD4148WTP / MBR15U150)** — crop 完全 skip，這 2 顆有 6 個 L/W/H 錯誤無法觸碰
2. **crop 範圍太寬時** — 一頁多個 dim 表（如 1N4148W 含多 variant），LLM 抽錯到別 variant
3. **GT vs LLM 結構性分歧** — BAV99W H, MSB30M W 不是 cropping 能解的（GT 跟 LLM 認知的 body 軸不同）

## 下一步假設（V22）

換 PDF extractor 到 `multimodal_toc`（PDF TOC 結構定位機械頁）。
比 V8 keyword grep 應該更精準，沒 TOC 的 PDF fallback 到原 keyword 流程。
