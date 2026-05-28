# Datasheet 參數提取系統（NTUST AI 期末作業）

從 10 份電子元件 datasheet PDF 自動提取 11 個結構化規格欄位，與 `data/specbook.xlsx` 標答比對計算準確率，並提供本機 webapp 上傳試用。

**最終準確率：105 / 110 = 95.5%（每個欄位皆 ≥ 80%）。**

四個任務怎麼完成、成果數據佐證與不過度擬合（not overfit）證明，詳見 **[REPORT.md](REPORT.md)**。

## 四個任務對應

1. **VLM 解析尺寸圖面** — PDF 光柵化成圖餵 GPT-4o 多模態看圖，Llama vision 複核長寬印反（pure swap）。
2. **強制 100% 合法 JSON** — API 層 JSON mode（Azure `response_format=json_object` / Ollama `format=json`），非 prompt 祈求。
3. **批次 10 筆、每欄 ≥ 50%** — 全跑 95.5%，逐欄正確率見 REPORT.md。
4. **本機 webapp** — `streamlit run app.py`，可上傳檔案即時試用。

## 環境需求

- Python 3.10+（已驗證 3.11.5）
- 本地推理：Ollama（可選）
- 雲端推理：Azure AI Foundry 訂閱（webapp 即時抽取需要）
- camelot 抽取需 Ghostscript（可選）

## 安裝

```powershell
pip install -r requirements.txt
pip install streamlit          # 任務四 webapp
```

## 設定

```powershell
Copy-Item .env.example .env
notepad .env   # 填值
```

`.env` 關鍵變數：

```bash
BACKEND=azure_gpt4o        # ollama / azure_gpt4o / azure_llama / azure_mistral
PDF_EXTRACTOR=multimodal   # pdfplumber / fitz / camelot / multimodal
```

雲端模型需另填 `AZURE_FOUNDRY_ENDPOINT` + `AZURE_FOUNDRY_KEY`，詳見 `AZURE_SETUP.md`。

## 執行

```powershell
# 1. 評估最終成果（不重跑 LLM，純比對已存結果，列各版本準確率）
python evaluate_all.py

# 2. 啟動 webapp（任務四）
streamlit run app.py          # 本機 http://localhost:8501
```

webapp 兩個區塊：
- **區塊一「10 顆 SPEC 示範成果」**：讀已跑好結果，秒出、零 API、逐格對照標答（紅底為錯格），可收合。
- **區塊二「上傳 PDF 即時跑」**：拖多檔當場端到端抽取（GPT-4o 看圖 + Llama swap 偵測）。即時版為單模型約 80%，非完整 V47；需 Azure 金鑰。

## 目錄結構

```
20260508_期末作業/
├── app.py              任務四 webapp（Streamlit）
├── REPORT.md           成果報告（四任務 + 數據佐證）
├── main.py             主流程：抽取 + 雙 agent 迭代 + 比對
├── prompts.py          集中管理 prompt 與 11 欄位規則
├── pdf_extractor.py    PDF 解析抽象（pdfplumber/fitz/camelot/multimodal 可切換）
├── llm_backend.py      LLM 後端抽象（Ollama/Azure GPT-4o/Llama/Mistral 可切換）
├── validators.py       後處理：單位修正、sanity check
├── config.py           路徑、欄位、比對閾值
├── evaluate_all.py     統一評估所有版本準確率
├── run_v*.py           各版本迭代腳本（V4 ~ V48）
├── .env.example        環境變數範本
├── AZURE_SETUP.md      Azure AI Foundry 部署教學
├── requirements.txt
├── data/specbook.xlsx  標答
├── datasheets/         10 份 PDF
└── output/_archive/    各版本完整歸檔（可回溯、可重現）
```

## 提取欄位（共 11 項）

| # | 欄位 | 型別 |
|---|---|---|
| 1 | Part Number | str（指定型號，直接填） |
| 2 | Minimum Operating Temperature(°C) | int |
| 3 | Maximum Operating Temperature (°C) | int |
| 4 | Maximum Length (mm) | float |
| 5 | Maximum Width (mm) | float |
| 6 | Maximum Height (mm) | float |
| 7 | PIN Number | int |
| 8 | I_O、I_F (A) | float |
| 9 | V_F(Forward Voltage) (V) | str（多測試條件） |
| 10 | V_RRM(Peak Repetitive Reverse Voltage) (V) | int |
| 11 | I_R(Reverse Current) | str（多測試條件） |

## 比對規則

| 欄位類型 | 規則 |
|---|---|
| 數值（溫度、尺寸、I_O/I_F） | ±5% 容差 |
| 完全相符（Part Number、V_RRM、PIN） | 字串完全相等 |
| 文字組合（V_F、I_R） | 全形頓號拆 token，集合命中率 ≥ 50% |
