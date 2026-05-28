# 用本地 LLM 從 Datasheet PDF 提取電子元件參數

台科 AI 課程 2026/05/08 期末作業。

從 10 份電子元件 datasheet PDF 自動抽取 11 個結構化欄位，輸出 JSON / CSV，並與 `specbook.xlsx` 標準答案比對計算準確率。

**核心原則：所有推理 100% 在本地完成，資料不上雲。**

---

## 為什麼用本地模型

| 考量 | 說明 |
|---|---|
| 資料安全 | Datasheet 對部分公司屬商業敏感資料，避免上傳第三方雲端 |
| 成本可控 | Ollama 一次安裝，後續推理無 API 費用 |
| 離線運作 | 內網 / 工廠環境仍能使用 |
| 可審計 | 所有 prompt、回應、模型權重皆在本機，可完整追蹤 |

---

## 環境需求

- Python 3.10+（已驗證 3.11.5）
- Ollama（本地 LLM runtime）
- 至少 8GB RAM（跑 7B 量化模型）

---

## 安裝步驟

### 1. 安裝 Ollama

下載：<https://ollama.com/download>

Windows 執行 `OllamaSetup.exe`，安裝後 Ollama 會以背景服務常駐 port 11434。

### 2. 下載模型

```powershell
ollama pull qwen2.5:7b
```

約 4.7GB。

### 3. 安裝 Python 套件

```powershell
pip install -r requirements.txt
```

---

## 執行方式

```powershell
python main.py
```

執行流程：
1. 載入 `data/specbook.xlsx` 標答
2. 逐份 PDF 用 pdfplumber 抽文字 + 表格（過長時挑第 1 頁 + 含關鍵字頁）
3. 把文字塞進 prompt 餵給 Ollama，要求只輸出 JSON
4. 收 JSON → 寫入 `output/results.json` 與 `output/results.csv`
5. 跟標答比對 → 輸出 `output/accuracy_report.md`

10 顆 PDF 在 CPU 上約需 5-10 分鐘。

---

## 目錄結構

```
20260508_期末作業/
├── main.py                # 主程式（PDF 抽取 + LLM 呼叫 + 評估 + 報告）
├── prompts.py             # Prompt 模板
├── config.py              # 路徑、模型、欄位定義
├── requirements.txt
├── README.md
├── data/
│   └── specbook.xlsx      # 標準答案
├── datasheets/            # 10 份 PDF
└── output/                # 執行後產出
    ├── results.json
    ├── results.csv
    └── accuracy_report.md
```

---

## 提取欄位（共 11 項）

| # | 欄位 | 型別 | 說明 |
|---|---|---|---|
| 1 | Part Number | str | 元件編號 |
| 2 | Minimum Operating Temperature(°C) | int | Tj/Operating Temp 下限（不含 Storage） |
| 3 | Maximum Operating Temperature (°C) | int | Tj/Operating Temp 上限 |
| 4 | Maximum Length (mm) | float | 封裝外觀長度 MAX |
| 5 | Maximum Width (mm) | float | 封裝外觀寬度 MAX |
| 6 | Maximum Height (mm) | float | 封裝外觀高度 MAX |
| 7 | PIN Number | int | 封裝針腳數 |
| 8 | I_O、I_F (A) | float | 平均整流輸出電流 / 順向電流，單位統一為 A |
| 9 | V_F(Forward Voltage) (V) | str | 順向電壓，含所有測試條件 |
| 10 | V_RRM(Peak Repetitive Reverse Voltage) (V) | int | 峰值重複反向電壓 |
| 11 | I_R(Reverse Current) | str | 反向電流，含單位（uA/nA/mA）與條件 |

---

## 比對規則

| 欄位類型 | 比對方法 |
|---|---|
| 數值（溫度、尺寸、I_O/I_F）| 容差 ±5% |
| 完全相符（Part Number、V_RRM、PIN Number）| 字串完全一致 |
| 文字組合（V_F、I_R）| 用 `、` 拆 token，集合命中率 ≥ 50% 算通過 |
