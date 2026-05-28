# V20 — 提升截圖 zoom + Package Outline 強制優先

> Date: 2026-05-22
> Base version: V12 (84.5% train, 100% holdout)
> Hypothesis: 高 zoom (3.5→4.5) + High precision 頁面送 LLM 前面，能讓 vision 看清 Package Outline 表內 D/E/A Max 欄

## 改動內容

純 generic — 不依賴 train set 內容：
- `pdf_extractor.py` `_RASTER_ZOOM`：固定 3.5 → 由 env `RASTER_ZOOM` 控制，V20 設 4.5
- `pdf_extractor.py` 選頁順序：新增 env `IMAGE_ORDER=precision`，命中 high precision 關鍵字的頁送 LLM 前面（vision attention 對前面 image 較高）
- `run_v20.py`：driver 設 `RASTER_ZOOM=4.5` + `IMAGE_ORDER=precision`，其他配置與 V12 同

## 為什麼這不是 overfit

**規則 1：改動 generic — 不依賴 train set 元件名**

- [x] prompt / code 沒寫 `BAV99W` / `DFLS160` / `MSB30M` 等 train set 元件名
- [x] 沒寫 train set 內具體錯誤數值（2.2 / 1.93 等）
- [x] 改動是 PDF 處理機制，不是答案表

**規則 2：train + holdout 不退步**

| 指標 | Train | Holdout | Gap | 判定 |
|---|---|---|---|---|
| V12 baseline | 93/110 = 84.5% | 55/55 = 100% | -15.5% | — |
| V20 this iter | **92/110 = 83.6%** | **55/55 = 100%** | -16.4% | **FAIL (train ↓ 0.9%)** |

**Overfit 判定：** 不是 overfit（train ↓ 但 holdout 持平 100%）。**是 regression** — 改動傷害 train 不改善 holdout。

## V20 結論

**失敗 — 回退到 V12 配置作 baseline。**

純 image 處理參數（zoom、頁序）對 train accuracy 沒幫助，反而可能讓 vision 注意力分散。
代表「機械尺寸抽錯」的瓶頸**不在 image 解析度**，而是 vision model 的 **判斷邏輯**：
- 看到 Package Outline + Footprint 兩張表時選錯
- L/W 互換因為 D/E 符號識別錯

## 下一步假設（V21）

**換方向：Crop-based deep dive on L/W/H cells**

不對整頁送圖，改成：
1. 用 V12 配置先跑 baseline answer
2. 對 L/W/H 三個機械尺寸欄位，用 PyMuPDF `page.search_for("Package Outline")` 找 anchor bbox
3. crop 該 bbox 高 zoom (5x) 區塊圖
4. 帶 cropped 圖 + 「**只問 L/W/H**」的窄 prompt 給 LLM 重抽
5. 取代原 L/W/H answer

generic — 對所有 PDF 都套同流程。預期效益：強制 LLM 看「Package Outline 區塊」而非整頁，消除 footprint 混淆。
