> WARNING **更正聲明（2026-05-28 OVERFIT audit）**
>
> 本文件下方若有「V47 NOT OVERFIT」「holdout 92.7%」「95.5% 不 overfit」等結論，均已被推翻。
> 評分集只有 10 份 spec；V37 起（含 V44 95.5%、最終 V47）的後處理規則門檻是逐顆 spec 反推的，屬對評分集 overfit。
> 完整逐版判定見專案根目錄 `OVERFIT_AUDIT.md`。乾淨可交版本：V23（85.5%）或 V31（89.1%，需註明為不加 part-specific 規則的上限）。

---

# 實驗報告：Datasheet 參數提取的 LLM 與 PDF 抽取方法效能評估

**日期區間**：2026-05-08 ~ 2026-05-10
**作者**：黃姿晴（user08@NTUSTAI）
**課程**：NTUST AI 期末作業

---

## 1. 摘要 (Abstract)

本實驗以「電子元件 datasheet PDF 自動參數提取」為任務，系統性比較**兩個自變數**對準確率的影響：(A) PDF 文字抽取方法（pdfplumber / PyMuPDF-fitz / camelot-py）、(B) LLM 模型容量（5 個模型，本地 qwen2.5:7b/14b 至雲端 GPT-4o / Llama-4-Maverick / Mistral-medium-2505）。

**主要發現**：模型升級為效能主槓桿（+12%），PDF 抽取方法為次要（±4%）。最佳組合 **pdfplumber × GPT-4o = 76.4%**，與 Mistral-medium-2505 並列冠軍。三家雲端模型呈現**強項分化**：GPT-4o 為 multi-product datasheet 王、Mistral 為橋式整流器王、Llama-4 為簡單表格王。理論 ensemble 上限為 80.9%。

---

## 2. 實驗目的

1. **量化** PDF 抽取方法對 LLM 提取準確率的因果影響
2. **量化** LLM 容量升級的邊際效益
3. **比較** 兩個槓桿的相對重要性，給出工程建議
4. **建立** 不同模型在不同 datasheet 結構下的強弱分化表

---

## 3. 實驗設計

### 3.1 控制變因（Fixed Variables）

| 控制項 | 值 |
|---|---|
| 任務 | 從 10 份 datasheet 抽 11 個結構化欄位 |
| Ground Truth | `specbook.xlsx`（外部給定標答） |
| 比對邏輯 | 數值 ±5% 容差 / 字串完全相等 / token 集合 ≥50% |
| Prompt | V2 iter3 定型版（含 placeholder 防污染、L/W/H chain-of-thought） |
| 後處理 | `validators.py`（mV→V 換算、L/W/H 範圍檢查、Tmin/max 互換、PIN 合理化、I_O 換算） |
| Temperature | 0（確定性輸出） |
| Context window | 16384 tokens (Ollama) |
| PDF 字元上限 | 12000 |

### 3.2 自變數（Independent Variables）

**Axis A — PDF 抽取方法**：

| Extractor | Paradigm | 特點 |
|---|---|---|
| pdfplumber | General | extract_text() + extract_tables() flatten |
| PyMuPDF (fitz) | General | get_text() + find_tables()（PyMuPDF 1.23+） |
| camelot-py | Table-specific | lattice + stream 雙模式 + pdfplumber 補 narrative text |

**Axis B — LLM 模型**：

| Model | Provider | 部署 | 容量 |
|---|---|---|---|
| qwen2.5:7b (Q4_K_M) | Alibaba | Local Ollama | 7B 量化 |
| qwen2.5:14b (Q4_K_M) | Alibaba | Local Ollama | 14B 量化 |
| GPT-4o | OpenAI | Azure Foundry V1 | ~200B+（推估） |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | Meta | Azure Foundry serverless | 17B active / 400B total (MoE) |
| mistral-medium-2505 | Mistral AI | Azure Foundry serverless | 中型（廠商未公開） |

### 3.3 應變變數（Dependent Variables）

- **主**：整體準確率 = Σ(命中欄位) / Σ(總欄位) = X / 110
- **次**：各元件準確率（X / 11）
- **質性**：各欄位錯誤類型分布（用於分析強弱項）

### 3.4 實驗矩陣（十字設計）

```
                pdfplumber     fitz       camelot
qwen 7b           61.8%(*)      —          —
qwen 14b         64.5% ⚓     63.6%      60.9%      ← Phase 1 (PDF axis)
GPT-4o           76.4% ⭐                            ← Phase 2 (Model axis)
Llama-4-Maverick 72.7%
mistral-med-2505 76.4% ⭐
```

⚓ = baseline, ⭐ = best, (*) = 7b 同時搭配 V2 iter3 prompt + validator
6 個獨立 cells（pdfplumber × 14b 由 Phase 1 與 Phase 2 共用作 cross-axis anchor）。

完整 3×5 = 15 cells 為 fractional factorial 不必要，**十字設計足夠分離主效應**。

---

## 4. 結果

### 4.1 整體準確率對照表

| Cell | PDF Extractor | LLM | 整體 |
|---|---|---|---|
| Phase 1.1 | pdfplumber | qwen2.5:14b | **64.5%** ⚓ |
| Phase 1.2 | fitz | qwen2.5:14b | 63.6% |
| Phase 1.3 | camelot | qwen2.5:14b | 60.9% |
| Phase 2.1 | pdfplumber | qwen2.5:7b | 61.8% |
| Phase 2.2 | pdfplumber | **GPT-4o** | **76.4%** ⭐ |
| Phase 2.3 | pdfplumber | Llama-4-Maverick | 72.7% |
| Phase 2.4 | pdfplumber | **mistral-medium-2505** | **76.4%** ⭐ |

### 4.2 各元件 × 各 Cell 對戰矩陣

| Part | qwen7b | qwen14b | GPT-4o | Llama-4 | Mistral | 最佳 |
|---|---|---|---|---|---|---|
| 1N4148W | 8 | 8 | **9** | **9** | **9** | 9/11 |
| BAS16 | 6 | 8 | **9** | 8 | 8 | 9/11 |
| BAS21H | 6 | 8 | 8 | 8 | 8 | 8/11 |
| BAT750 | 8 | 7 | **10** | 9 | 9 | 10/11 |
| BAV99W | 6 | 6 | **7** | **7** | 6 | 7/11 ⚠ |
| CD4148WTP | 8 | 8 | 8 | **11** | **11** | 11/11 ⭐ |
| DFLS160 | 8 | 7 | **9** | **9** | 8 | 9/11 |
| **MBR15U150** | 1 | 4 | **7** | 2 | 6 | 7/11 ⚠ |
| MSB30M | 8 | 5 | 7 | 7 | **9** | 9/11 |
| SBR05U20LPS | 9 | 10 | **10** | **10** | **10** | 10/11 |
| **TOTAL** | **68** | **71** | **84** | **80** | **84** | — |
| **%** | **61.8%** | **64.5%** | **76.4%** | **72.7%** | **76.4%** | — |

⚠ = 即便最佳模型也卡關（疑似標答錯誤或結構性難題）
⭐ = 達到滿分

### 4.3 PDF axis（固定 14b）詳表

| 元件 | pdfplumber | fitz | camelot |
|---|---|---|---|
| 1N4148W | 8 | 7 | 8 |
| BAS16 | 8 | 7 | 8 |
| BAS21H | 8 | 8 | 8 |
| BAT750 | 7 | 7 | 5 |
| BAV99W | 6 | 6 | 5 |
| CD4148WTP | 8 | **10** | **9** |
| DFLS160 | 7 | 7 | 8 |
| MBR15U150 | 4 | 3 | 3 |
| MSB30M | 5 | 7 | **7** |
| SBR05U20LPS | **10** | 8 | 6 |
| **TOTAL** | **71** | **70** | **67** |

---

## 5. 分析

### 5.1 主效應 1：PDF 抽取方法（弱負）

固定 14b、變動 PDF 方法的範圍是 60.9% ~ 64.5%，**極差 3.6%**。

- 預期 camelot（table-specific）會在 mechanical drawing 表現好 → **未獲驗證**
- camelot 反而最差（-3.6%），fitz 略差於 pdfplumber（-0.9%）

**根因推測**：camelot 抽出字數約 9700（pdfplumber 5400），**幾乎兩倍**，過量資訊稀釋 LLM 對關鍵欄位的注意力（attention dilution）。同樣 PDF 表格在 fitz 抽取相對精簡但缺少 pdfplumber 對段落結構的保留。

**個別元件互動**：

- camelot 在 MSB30M（橋式整流，有線框電氣表）+2、CD4148WTP +1
- fitz 在 CD4148WTP 跳到 10/11
- 但 SBR05U20LPS、BAT750、BAV99W 在非 pdfplumber 上明顯退步

**結論**：**沒有單一最佳 PDF 方法**，per-PDF 互動明顯，但整體 pdfplumber 最穩。

### 5.2 主效應 2：LLM 模型容量（強正）

固定 pdfplumber、變動模型的範圍是 61.8% ~ 76.4%，**極差 14.6%**。

```
  qwen 7b → qwen 14b      :  +2.7%   (同族大小升級)
  qwen 14b → Llama-4      :  +8.2%   (跨族 + MoE)
  qwen 14b → Mistral-med  : +11.9%   (跨族,中型 dense)
  qwen 14b → GPT-4o       : +11.9%   (跨族,旗艦級)
```

**結論**：**模型升級是主要效能槓桿**，從本地量化模型跳到雲端大模型可帶來雙位數提升。

### 5.3 兩個槓桿的相對效益比較

```
  PDF axis 極差:  3.6%
  Model axis 極差: 14.6%
  比率: ~ 4:1 偏向模型升級
```

**工程意涵**：時間預算有限時，**先換模型 / 後改 PDF**。改 PDF 抽取的邊際效益遠不如換更強模型。

### 5.4 三家雲端模型強項分化

| 元件 | GPT-4o | Llama-4 | Mistral | 觀察 |
|---|---|---|---|---|
| BAT750 | **10** | 9 | 9 | GPT-4o 強 |
| CD4148WTP | 8 | **11** | **11** | Llama / Mistral 滿分,GPT-4o 反而不行 |
| MBR15U150 | **7** | 2 | 6 | GPT-4o 大幅領先,Llama 慘敗 |
| MSB30M | 7 | 7 | **9** | Mistral 強 |

**三大發現**：

(a) **GPT-4o 在 multi-product datasheet 上獨強**（MBR15U150 7/11 vs Llama 2/11） — 推測超大 dense 容量讓它能維持「型號鎖定」 attention，不被同檔內其他變體誤導
(b) **Llama-4-Maverick MoE 17B active 在 MBR15U150 大幅退步**（甚至比本地 qwen14b 還差） — MoE active param 過小可能無法處理長 multi-product context
(c) **CD4148WTP 對 Llama / Mistral 特別友善**，雙雙 11/11 滿分；GPT-4o 反而 8/11，原因待研究

### 5.5 MBR15U150：模型容量的單一指標

```
  qwen 7b:        1/11   ← 完全崩潰
  qwen 14b:       4/11   ← 部分恢復
  Llama-4-Mav:    2/11   ← 退步
  Mistral-med:    6/11   ← 中等
  GPT-4o:         7/11   ← 最佳但仍非滿分
```

**MBR15U150 的 PDF 內含多個型號變體**（MBR15U060/080/150，不同 V_RRM 等級）。模型必須在「同一份 PDF 內鎖定指定型號的那一列」並抽取對應參數。**這是 dense capacity 的試金石** — 模型越大，越能維持長 context 的型號鎖定不被干擾。

### 5.6 理論 Ensemble 上限（不可實用）

若每個元件取三家雲端最佳：

```
9 + 9 + 8 + 10 + 7 + 11 + 9 + 7 + 9 + 10 = 89/110 = 80.9%
```

但這是 **per-PDF best-of-3 cherry-pick**，屬於 train set overfit，沒有泛化價值。實務上若沒有 ground truth，無法事先知道哪家最好。**真實生產上限** = 單一最佳模型 = **76.4%（GPT-4o 或 Mistral）**。

---

## 6. 結論

### 6.1 主要發現

1. **模型升級的效益是 PDF 抽取方法升級的約 4 倍**（極差比 14.6% : 3.6%）
2. **本地 qwen2.5:14b（64.5%）→ 雲端 GPT-4o / Mistral（76.4%）**為主要躍升點
3. **PDF 抽取方法無單一最佳**，per-PDF 互動明顯，但 pdfplumber 整體最穩
4. **三家雲端模型 76% 左右並列**，差別在「強項分化」而非「整體實力」
5. **MBR15U150（multi-product datasheet）是模型容量的單一試金石** — 區分大模型與超大模型

### 6.2 工程意涵

| 預算 | 建議 |
|---|---|
| 限本地推理 | qwen2.5:14b + pdfplumber + V2 iter3 prompt + validator 為最佳組合（64.5%） |
| 可上雲 | 直接 GPT-4o 或 Mistral-medium，不必再花時間改 PDF / prompt（76.4%） |
| 想極限優化 | 多模態（GPT-4o vision 餵 mechanical drawing 圖片）或 ensemble（per-PDF 投票），尚未測試 |

### 6.3 局限

1. **樣本太小**：N=10 顆元件，統計顯著性不足以做正式假設檢定（t-test / ANOVA）
2. **PDF 方法局限於文字抽取**：未測試多模態（直接送 PDF 渲染圖給視覺模型）
3. **prompt 已固定**：未做 model × prompt 交互（每個模型可能對 prompt 風格敏感度不同）
4. **76% 的天花板來源未細究**：可能是 prompt 設計、輸入訊息品質、或標答本身的歧義（V1 已標註 BAV99W 兩欄疑似標答錯）

### 6.4 未來方向

1. **多模態實驗**：用 GPT-4o vision 直接餵 mechanical drawing 頁的圖片，攻 L/W/H 痛點
2. **DSPy 自動化 prompt 優化**：用 train/val 切分自動搜尋 prompt 變體
3. **LoRA fine-tuning**：若能收集 100+ 標註資料，做 qwen 7b LoRA 看本地能否突破 70%
4. **驗證標答**：BAV99W 兩欄疑似錯誤，請助教確認（會把上限從 110 拉到實際可達天花板）

---

## 7. 附錄

### A. V1（已提交版）

| 項目 | 值 |
|---|---|
| 模型 | qwen2.5:7b (Q4_K_M) |
| PDF 方法 | pdfplumber |
| 整體 | 67/110 = **60.9%** |
| 詳細報告 | `_archive/v1_qwen7b/accuracy_report.md` |

### B. V2 Prompt Iteration（7 輪）

| Iter | Prompt 變動 | qwen 7b 整體 |
|---|---|---|
| 0 | 從零盲設計版 | 60.0% |
| 1 | placeholder 化（防範例污染） | 60.0% |
| 2 | L/W/H chain-of-thought | 60.9% |
| 3 | + validators.py 後處理 | **61.8% (7b 最佳)** |
| 4 | + datasheet 章節導航 | 58.2% ❌ |
| 5 | 兩段式 LLM call | 51.8% ❌ |
| 6 | 換 14b 模型（prompt 凍結 iter3） | **64.5%（過渡到 Phase 1）** |

iter 4-5 退步驗證了「prompt 工程在小模型上有 ~62% 天花板」假說。

### C. 各 Cell 完整錯誤分析

每個 cell 的逐欄錯誤詳情存於：
- `_archive/v2_pdfplumber_azure_gpt_4o/errors_detail.json`
- `_archive/v2_pdfplumber_azure_llama_4_maverick/errors_detail.json`
- `_archive/v2_pdfplumber_azure_mistral_medium_2505/errors_detail.json`
- `_archive/v2_camelot_ollama_qwen2_5_14b/errors_detail.json`
- `_archive/v2_fitz_ollama_qwen2_5_14b/errors_detail.json`
- `_archive/v2_iter6_qwen14b/errors_detail.json`

完整 LLM 抽取原始 JSON 同資料夾 `results.json`。

### D. 環境與重現步驟

```
作業系統:     Windows 11
Python:       3.11.5
LLM 框架:     Ollama 0.x(本地) + OpenAI Python SDK 1.x(Azure)
PDF 工具:     pdfplumber 0.11.9 / PyMuPDF 1.27.2.3 / camelot-py 1.0.9
系統依賴:     Ghostscript 10.07.0(camelot lattice 模式必需)
雲端區域:     East US 2(Azure AI Foundry)
雲端模型:     GPT-4o (Global Standard) / Llama-4-Maverick (Serverless) / mistral-medium-2505 (Serverless)
```

重現指令：

```powershell
# 1. 安裝
pip install -r requirements.txt

# 2. 設 .env(從 .env.example 拷貝填值)
Copy-Item .env.example .env
# 編輯 .env: 填 BACKEND, PDF_EXTRACTOR, AZURE_FOUNDRY_ENDPOINT, AZURE_FOUNDRY_KEY 等

# 3. 跑單一 cell
python main.py
# (結果自動歸檔到 output/_archive/v2_<extractor>_<backend>/)
```

### E. 隱私聲明

V1 採本地推理。V2 Phase 2 採 Azure AI Foundry 託管推理，雖屬雲端但 Azure 企業條款保證輸入內容不被當訓練資料、abuse monitoring log 預設 30 天可申請關閉、region 鎖在 East US 2。對 datasheet 這類**公開但商業敏感**的內容已足夠；採用此方案的目的是建立準確率天花板對照。

### F. 已知標答疑似錯誤

V1 報告已標註：
- **BAV99W / Minimum Operating Temperature(°C)**：標答 150 但 datasheet 寫 -55（Tj/Tstg=-55~+150）
- **BAV99W / V_RRM**：標答 150 但 datasheet 寫 100 (V_RRM=100V)

兩欄即使最佳模型抽對也會被判錯。若助教確認標答錯誤，所有 cell 的分數應 +2 分（GPT-4o 從 84 → 86，新整體 = 78.2%）。

---

**報告結束**
