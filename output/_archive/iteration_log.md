# NTUST AI 期末作業 — V1 + V2 完整 Iteration Log

**日期區間**：2026-05-08 ~ 2026-05-10
**任務**：從 10 份電子元件 datasheet PDF 自動抽取 11 個結構化欄位

> **完整實驗分析**請見 `experiment_report.md`。
> 本檔是時間序的「我做了什麼」流水帳。

---

## 整體分數曲線

| 版本 | 模型 | 整體 | 變化 | 主要改動 |
|---|---|---|---|---|
| V1 (已交) | qwen2.5:7b | **67/110 = 60.9%** | baseline | 初版 prompt + 具體範例值 |
| V2 iter 0 | qwen2.5:7b | 66/110 = 60.0% | -0.9 | 從零盲設計版 prompt |
| V2 iter 1 | qwen2.5:7b | 66/110 = 60.0% | 0 | 範例值改 placeholder + 防污染警示 |
| V2 iter 2 | qwen2.5:7b | 67/110 = 60.9% | +0.9 | L/W/H 加 chain-of-thought + 修 V_F 過嚴 |
| V2 iter 3 | qwen2.5:7b | **68/110 = 61.8%** | +0.9 | ⭐ 加 validators.py 後處理 (7b 最佳) |
| V2 iter 4 | qwen2.5:7b | 64/110 = 58.2% | **-3.6** | ❌ 加 datasheet 章節導航 (失敗) |
| V2 iter 5 | qwen2.5:7b | 57/110 = 51.8% | **-10** | ❌ 兩段式 LLM call (失敗) |
| V2 iter 6 | qwen2.5:14b | **71/110 = 64.5%** | +2.7 | ⭐⭐ 換 14b 模型 (iter 3 prompt 不變) |

---

## V1 (已提交版) — qwen2.5:7b — 67/110 = 60.9%

### 各元件分數

| Part Number | 正確/總數 | 準確率 |
|---|---|---|
| 1N4148W | 9/11 | 81.8% |
| BAS16 | 7/11 | 63.6% |
| BAS21H | 6/11 | 54.5% |
| BAT750 | 8/11 | 72.7% |
| BAV99W | 6/11 | 54.5% |
| CD4148WTP | 8/11 | 72.7% |
| DFLS160 | 7/11 | 63.6% |
| MBR15U150 | 3/11 | 27.3% |
| MSB30M | 7/11 | 63.6% |
| SBR05U20LPS | 6/11 | 54.5% |

### 主要 Limitation（V1 報告原文）

1. **尺寸 (L/W/H)**：pdfplumber 對 mechanical drawing 表格 cell 拆解混亂，LLM 抓 NOM/TYP 而非 MAX
2. **Multi-product datasheet**：MBR15U150 PDF 含多型號變體，7B 量化模型抓錯主型號（抽到 "TO-277"）
3. **V_F / I_R 條件不齊**：標答列多測試條件時，LLM 只抽 1-2 個
4. **疑似標答錯誤**：BAV99W 兩欄（Min Op Temp 標答 150 vs datasheet -55、V_RRM 標答 150 vs datasheet 100）

> 完整逐欄錯誤明細見：`v1_qwen7b/accuracy_report.md`

---

## V2 全輪設計變更追蹤

### iter 0 — Baseline（從零盲設計版）

**改動**：完全不引用 V1 結果，純用 11 個欄位名稱 + EE 領域常識重建 prompt

**結果**：66/110 = 60.0%（與 V1 持平）

### iter 1 — Placeholder 化

**改動**：
- 範例值（如 `0.715 @1mA`）改成 `<v1> @<I1>mA` 占位符
- 開頭加「禁止抄範例值」警示

**動機**：iter 0 發現 LLM 在抽不到時會直接抄 prompt 範例值（污染問題），最嚴重的是 MBR15U150 V_F 完全等於 1N4148W 範例值

**結果**：66/110 = 60.0%（總分不變但內部分布大改，MBR15U150 從 4 → 2，BAV99W 從 5 → 7）

### iter 2 — L/W/H Chain-of-Thought

**改動**：
- L/W/H 規則加 5 步驟 chain-of-thought
- 點名排除 Land Pattern / Footprint / Tape & Reel
- 加 sanity check 範圍（0.8~10mm 等）
- 修 iter 1 副作用：把「V_F 不要超抽」改中性表述

**結果**：67/110 = 60.9%（+1，與 V1 同分）— L/W/H 沒實質改善，多出來那 1 分來自 V_F 條件數修正

### iter 3 — Validator 後處理層 ⭐

**改動**：新增 `validators.py`：
- V_F mV→V 自動換算（值 > 10 視為 mV）
- V_F / I_R 格式正規化（去 `T_J=`、`V_R=`、dc 後綴、μ→u）
- L/W/H sanity 範圍（0.2~15mm 外設 null）
- 溫度 Tmin > Tmax 自動互換
- PIN 必須 ∈ {2,3,4,8} 否則 null
- I_O > 100 視為 mA → ÷1000

**結果**：68/110 = **61.8%（7b 最佳）**

關鍵修正：
- BAS21H V_F：`1000 @100mA` → `1 @100mA` ✓
- BAT750 V_F：`340/390/420/475` → `0.34/0.39/0.42/0.475` ✓
- BAS16 / SBR05U20LPS / MSB30M 的條件格式統一

### iter 4 — Datasheet 章節導航 ❌

**改動**：在 prompt 中加入「章節導航表」+「跳過章節清單」+「抽取順序」共 30 行

**動機**：根據 PTT/EDN 的 datasheet 閱讀指引，告訴 LLM 去哪裡找

**結果**：64/110 = 58.2%（**-3.6**）

**失敗原因**：attention degradation。即使是高 density 資訊，prompt 變長後 7b 模型對其他欄位的注意力下降。MSB30M -2、1N4148W -1、BAT750 -1、DFLS160 -1。

### iter 5 — 兩段式 LLM Call ❌

**改動**：拆成兩個短 prompt：
- Stage 1: L/W/H + PIN
- Stage 2: Tj、I_O、V_F、V_RRM、I_R

**動機**：每段 prompt 都短，避免 attention degradation

**結果**：57/110 = 51.8%（**-10**）

**失敗原因**：
1. 失去 cross-field consistency（V_F 單位與 mm 單位互相錨定的效應消失）
2. 短 prompt 為了短犧牲了規則密度，剛好 BAS21H、1N4148W 那些 case 需要的細節被刪
3. 2× LLM call = 2× hallucination 機率，MBR15U150 還是 1/11

### iter 6 — 換 qwen2.5:14b 模型 ⭐⭐

**改動**：
- prompt 回滾到 iter 3 狀態（單段 unified prompt）
- main.py 回到單次 LLM call + validator
- config.py：`OLLAMA_MODEL = "qwen2.5:14b"`

**結果**：71/110 = **64.5%（整體最佳）**

| 元件 | 7b iter3 | 14b iter6 | 變化 |
|---|---|---|---|
| MBR15U150 | 1/11 | **4/11** | +3 ⭐ multi-product 突破 |
| BAS16 | 6/11 | **8/11** | +2 |
| BAS21H | 6/11 | **8/11** | +2 |
| SBR05U20LPS | 9/11 | **10/11** | +1 ⭐ 接近滿分 |
| 1N4148W | 8/11 | 8/11 | = |
| BAV99W | 6/11 | 6/11 | = |
| CD4148WTP | 8/11 | 8/11 | = |
| BAT750 | 8/11 | 7/11 | -1 |
| DFLS160 | 8/11 | 7/11 | -1 |
| MSB30M | 8/11 | **5/11** | -3 |

推理時間：7b ~30 秒/顆 → 14b ~90 秒/顆（3x）

> iter 6 完整逐欄錯誤明細：`v2_iter6_qwen14b/errors_detail.json`
> iter 6 對應的 prompt / validator / config / main snapshot 同資料夾

---

## 從 7 輪實驗提煉的硬規律

1. **Prompt 改動有 ~62% 的天花板**：iter 1-5 都只在 58-62% 之間震盪，無論加 chain-of-thought、加章節導航、拆兩段都突破不了
2. **validator 後處理是最穩的招**：iter 3 的 +0.9 是唯一沒有副作用的提升
3. **7b 量化模型對 prompt 長度敏感**：超過某個臨界（約 200 行）就開始 attention degradation
4. **換更大模型才能突破天花板**：14b 直接 +2.7%，且 multi-product datasheet（MBR15U150）終於有反應
5. **prompt 範例值的具體數字會被抄**：placeholder 化是必修

---

## 歸檔結構

```
output/_archive/
├── iteration_log.md            ← 本檔
├── v1_qwen7b/                  ← V1 提交版（60.9%）
│   ├── accuracy_report.md      ← V1 完整逐欄錯誤分析
│   ├── results.json            ← V1 LLM 抽取原始輸出
│   ├── results.csv
│   └── README.md
└── v2_iter6_qwen14b/           ← V2 最佳（64.5%）
    ├── results_v2.xlsx         ← 含 Comparison sheet
    ├── results.json
    ├── errors_detail.json      ← 39 個錯誤的逐欄列表
    ├── prompts.py              ← iter 3 後定型的 prompt
    ├── validators.py           ← 後處理層
    ├── config.py               ← 14b 設定
    └── main.py                 ← pipeline
```

---

## 後續：科學方法雙軸實驗（已完成）

從「單軸 prompt iteration」升級為「雙軸 PDF × Model 矩陣」實驗，固定 prompt（V2 iter3 定型版）為控制變因。

### Phase 1：PDF 軸（固定 14b）

| Cell | PDF 方法 | 結果 |
|---|---|---|
| baseline | pdfplumber | 64.5%（與 iter6 共用） |
| Phase 1.2 | fitz | 63.6%（-0.9） |
| Phase 1.3 | camelot | 60.9%（-3.6） |

PDF 軸主效應**微弱**，pdfplumber 反而最穩。camelot 雖在簡單表格（CD4148WTP / MSB30M）有得，但過量輸出稀釋其他欄位 attention，整體退步。

### Phase 2：Model 軸（固定 pdfplumber）+ Azure Foundry V1

| Cell | LLM | 結果 |
|---|---|---|
| baseline | qwen2.5:14b（本地） | 64.5%（與 iter6 共用） |
| Phase 2.1 | qwen2.5:7b（本地，含 V2 iter3 prompt） | 61.8% |
| Phase 2.2 | **GPT-4o**（Azure Foundry V1） | **76.4%（+11.9）⭐** |
| Phase 2.3 | Llama-4-Maverick-17B-128E-Instruct-FP8 | 72.7%（+8.2） |
| Phase 2.4 | **mistral-medium-2505** | **76.4%（+11.9）⭐** |

**Model 軸主效應極強**，雲端大模型一步 +12%。

### 兩個槓桿的相對效益

| 槓桿 | 極差 | 結論 |
|---|---|---|
| PDF axis | 3.6% | 微弱 |
| Model axis | 14.6% | 強 |

**模型升級 vs PDF 改良 ≈ 4:1**

### Azure 三家強項分化

| 元件 | 冠軍 | 備註 |
|---|---|---|
| BAT750 | GPT-4o (10/11) | 一般電氣參數 |
| **CD4148WTP** | Llama-4 + Mistral 並列 (11/11) | **首見滿分** |
| **MBR15U150** | GPT-4o (7/11) | multi-product 殺手 |
| MSB30M | Mistral (9/11) | 橋式整流 |
| 其他元件 | 三家持平 | — |

理論 ensemble 上限 80.9%（per-PDF best-of-3，overfit 不可實用）；
單一最佳模型上限 = **76.4%（GPT-4o 或 Mistral）**。

---

## 完整 8 輪整體分數曲線（時間序）

```
V1 提交版    7b  pdfplumber                  60.9%
V2 iter 0    7b  pdfplumber  (盲設計)        60.0%
V2 iter 1    7b  pdfplumber  (placeholder)   60.0%
V2 iter 2    7b  pdfplumber  (CoT)           60.9%
V2 iter 3    7b  pdfplumber  (validator)     61.8% ⭐ 7b 最佳
V2 iter 4    7b  pdfplumber  (section nav)   58.2% ❌
V2 iter 5    7b  pdfplumber  (兩段式)        51.8% ❌
V2 iter 6   14b  pdfplumber                  64.5% ⭐ 本地最佳
Phase 1.2   14b  fitz                        63.6%
Phase 1.3   14b  camelot                     60.9%
Phase 2.2   GPT-4o     pdfplumber            76.4% ⭐⭐ 整體最佳
Phase 2.3   Llama-4    pdfplumber            72.7%
Phase 2.4   Mistral    pdfplumber            76.4% ⭐⭐ 整體最佳
```

---

## 歸檔最終結構

```
output/_archive/
├── iteration_log.md            ← 本檔（時間序流水帳）
├── experiment_report.md        ← 主實驗報告（科學分析）
├── v1_qwen7b/                  ← V1 已提交版凍結（60.9%）
├── v2_iter6_qwen14b/           ← V2 本地最佳（64.5%）
├── v2_camelot_ollama_qwen2_5_14b/      ← Phase 1.3
├── v2_fitz_ollama_qwen2_5_14b/         ← Phase 1.2
├── v2_pdfplumber_azure_gpt_4o/         ← Phase 2.2 ⭐
├── v2_pdfplumber_azure_llama_4_maverick/  ← Phase 2.3
└── v2_pdfplumber_azure_mistral_medium_2505/  ← Phase 2.4 ⭐
```

每個資料夾內含：
- `results_v2.xlsx` — Excel 三 sheet（Results / Comparison / Summary）
- `results.json` — LLM 抽取原始輸出
- `errors_detail.json` — 逐欄錯誤列表
- `summary.txt` — 該 cell 整體 + 各元件分數
- (Phase 1/2 cells 額外有 prompt/validator/config/main snapshot)
