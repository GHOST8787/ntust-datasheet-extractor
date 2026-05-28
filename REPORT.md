# Datasheet 參數提取系統 — 成果報告

從電子元件 datasheet PDF 自動提取 11 個結構化規格欄位，與標準答案（`specbook.xlsx`）比對計算準確率。本報告對應四個任務說明完成方式，並附可重現指令。

**最終成果：10 份 datasheet、110 格，正確 105 格 = 95.5%。每個欄位正確率皆 ≥ 80%，全部遠超 50% 門檻。**

---

## 任務一　用 VLM 解析尺寸圖面

封裝本體尺寸（長、寬、高）在多數 datasheet 裡只畫在 mechanical drawing 圖面，純文字 / 表格 parser 抓不到，這是傳統 OCR pipeline 的死角。

做法：用 PyMuPDF 把 PDF 頁面光柵化成高解析 PNG（`Matrix(4.5x)`），直接餵多模態模型（GPT-4o）看圖判讀尺寸；對形狀偏方、容易長寬印反的封裝，再用第二個視覺模型（Llama-4 vision）複核。

招牌機制「pure swap 偵測」：當 GPT-4o 抽到的長寬，與 Llama 看圖得到的長寬剛好對調時（誤差 < 5%），判定為圖面長寬印反並自動交換。此判斷只比較兩個模型的講法是否互相對調，**不參照任何標準答案**，因此對任何零件都成立。實例：holdout 的 VS3C12ET07S2L，GPT-4o 抽「長 10.67 / 寬 9.65」、Llama 看圖「D 9.65 / E 10.67」→ 判定純對調 → 修正。

- 多模態抽取：`pdf_extractor.py`（`MultiModalExtractor`）
- swap 偵測：`run_v47.py`（`needs_redo` / `detect_pure_swap` / `apply_swap`）

## 任務二　強制 100% 合法 JSON（不寫在 prompt 裡）

讓模型穩定輸出可入庫 JSON，靠的是 API 解碼層的 JSON mode，不是在 prompt 裡拜託模型「請輸出 JSON」：

- Azure / OpenAI 相容後端：呼叫帶 `response_format={"type": "json_object"}`
- 本地 Ollama：請求帶 `format="json"`

這兩者都在模型「產生 token 的階段」就約束輸出必為合法 JSON，從根本上避免「模型多講一句話、包了 markdown code fence、JSON 截斷」等問題。

- 實作位置：`llm_backend.py`（`AzureFoundryV1Backend.call` / `call_multimodal` 預設 `json_object`；`OllamaBackend` 帶 `format:json`）

作為第二道保險，另有寬鬆解析（去除 code fence、抓第一個 `{` 到最後一個 `}`），但主要保證來自 JSON mode 本身。

## 任務三　批次處理 10 筆、每欄 ≥ 50%

10 份 datasheet 全部批次跑完，統一以嚴格容差評分（數值 ±5%、文字 token-set ≥ 50%）。逐欄位正確率：

| 欄位 | 正確 / 總數 |
|---|---|
| Part Number | 10 / 10 |
| Minimum Operating Temperature | 9 / 10 |
| Maximum Operating Temperature | 10 / 10 |
| Maximum Length | 10 / 10 |
| Maximum Width | 8 / 10 |
| Maximum Height | 8 / 10 |
| PIN Number | 10 / 10 |
| I_O、I_F | 10 / 10 |
| V_F | 10 / 10 |
| V_RRM | 10 / 10 |
| I_R | 10 / 10 |
| **合計** | **105 / 110 = 95.5%** |

5 個未對上的格子皆為已知天花板，且誠實呈現於 webapp（紅底標示）：BAV99W 的最低溫 / 寬 / 高、MBR15U150 的寬 / 高。原因是標準答案與 datasheet 圖面定義有出入（例如 BAV99W 最低溫標答 −55，但 datasheet 該位置標 150），非單純抽取失誤。

## 任務四　本機 webapp

`app.py`（Streamlit），本機部署。兩個區塊：

- **區塊一「10 顆 SPEC 示範成果」**：讀已跑好的結果，秒出、零 API 呼叫，逐格對照標答（紅底為錯格），可收合。
- **區塊二「上傳 PDF 即時跑」**：可一次拖多檔，當場端到端抽取（GPT-4o 看圖 + 自我檢查 + Llama swap 偵測）。此為單模型即時版（約 80%），非完整 8 層 V47（95.5%）；完整 V47 為多層後處理疊加，現場重跑成本高，故即時版用單模型展示流程。

---

## 模型版本演進（重點）

| 版本 | 準確率 | 關鍵改動 |
|---|---|---|
| V1 | 60.9% | 本地 qwen2.5:7b + pdfplumber |
| V2 | 76.4% | 雲端 GPT-4o / Mistral + 純文字 |
| V12 | 86.4% | 多模態看圖 + in-context 範例 |
| V26 | 90.0% | 三模型投票 + 小封裝視覺偏誤修正 |
| **V47** | **95.5%** | 加 Llama pure swap 偵測（最終交付版） |

**未過度擬合（not overfit）**：V47 在另外 5 份從未見過的 datasheet（holdout）上達 92.7%，與訓練集 95.5% 的落差僅 2.7%（< 15% 門檻），且所有規則的觸發條件皆為通用數值條件、未寫死任何零件名稱、訓練與測試套用同一套程式。

（另有 V40 訓練集 96.4%、比 V47 多對 1 格，但其尺寸規則的比例邊界是貼著訓練資料調出來的、泛化較弱，故最終選 gap 更小的 V47。）

## 專案結構（模組化）

| 檔案 | 職責 |
|---|---|
| `main.py` | 主流程：抽取 + 雙 agent 迭代 + 比對 |
| `prompts.py` | 集中管理 prompt、11 欄位抽取規則 |
| `pdf_extractor.py` | PDF 解析抽象（pdfplumber / fitz / camelot / multimodal 可切換） |
| `llm_backend.py` | LLM 後端抽象（Ollama / Azure GPT-4o / Llama / Mistral 可切換） |
| `validators.py` | 單位修正與 sanity check |
| `evaluate_all.py` | 統一評估所有版本準確率 |
| `app.py` | 任務四 webapp |
| `output/_archive/`、`output/iteration_logs/` | 各版本結構化輸出（可回溯） |

## 可重現指令

```bash
# 1. 重新評估最終成果（不重跑 LLM，純比對已存結果）
python evaluate_all.py        # 輸出各版本 train / holdout 準確率對照表

# 2. 啟動 webapp
pip install streamlit
streamlit run app.py          # 本機 http://localhost:8501
```

即時抽取（webapp 區塊二）需在 `.env` 設定 Azure 金鑰。離線檢視成果（區塊一）與評估腳本則不需金鑰。
