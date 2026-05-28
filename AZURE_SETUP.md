# Azure 三模型銜接設置指南

跑 GPT-4o（Azure OpenAI）+ Llama 3.1 405B + Mistral Large 2（Azure AI Foundry serverless），對照本地 qwen2.5:14b 的 64.5% baseline。

---

## 一、安裝套件

```powershell
pip install -r requirements.txt
```

新增的依賴：
- `python-dotenv` — 讀 `.env`
- `openai` — Azure OpenAI 用同一 SDK
- `azure-ai-inference` + `azure-core` — Foundry serverless 模型

---

## 二、Azure portal 端設置

### 步驟 1：建 Azure AI Foundry hub + project

1. Azure portal → 搜尋「Azure AI Foundry」→ 建 hub（region 選 **East US 2** 或 **Sweden Central**，這兩區 Foundry 模型最齊）
2. 在 hub 內建一個 project

### 步驟 2：部署 GPT-4o（透過 Azure OpenAI）

1. Azure portal → 搜尋「Azure OpenAI」→ 建一個 OpenAI resource（**同一 region** 為佳）
2. 進 Azure OpenAI Studio → Deployments → Create new deployment
3. Model: `gpt-4o`，Deployment name 建議寫 `gpt-4o`（之後填 .env 用）
4. 從 resource 的「Keys and Endpoint」頁拿：
   - `AZURE_OPENAI_ENDPOINT`（如 `https://my-aoai.openai.azure.com`）
   - `AZURE_OPENAI_API_KEY`（KEY 1 或 KEY 2 任一）

### 步驟 3：部署 Llama 3.1 405B（Foundry serverless）

1. Azure AI Foundry portal → 你的 project → Models + endpoints → Model catalog
2. 搜「Meta-Llama-3.1-405B-Instruct」→ Deploy → 選 **Serverless API**
3. 同意 Meta 條款 → Deploy
4. 部署完進「Endpoints」頁拿：
   - `AZURE_LLAMA_ENDPOINT`（形如 `https://Meta-Llama-3-1-405B-Instruct-xxx.eastus2.models.ai.azure.com`）
   - `AZURE_LLAMA_KEY`

### 步驟 4：部署 Mistral Large 2407（Foundry serverless）

1. 同 Foundry portal → Models catalog
2. 搜「Mistral-large-2407」→ Deploy → Serverless API
3. 部署完拿：
   - `AZURE_MISTRAL_ENDPOINT`
   - `AZURE_MISTRAL_KEY`

---

## 三、`.env` 設置

```powershell
Copy-Item .env.example .env
notepad .env
```

把上面四組值（GPT-4o 的 endpoint+key+deployment、Llama 的 endpoint+key、Mistral 的 endpoint+key）填進去。

---

## 四、跑三輪

```powershell
# Round 1: GPT-4o
$env:BACKEND="azure_gpt4o"; python main.py

# Round 2: Llama 3.1 405B
$env:BACKEND="azure_llama"; python main.py

# Round 3: Mistral Large 2407
$env:BACKEND="azure_mistral"; python main.py
```

或者直接改 `.env` 的 `BACKEND=` 那行。

每輪跑完會自動歸檔到：
- `output/_archive/v2_azure_gpt_4o/`
- `output/_archive/v2_azure_llama_3_1_405b/`
- `output/_archive/v2_azure_mistral_large/`

---

## 五、預估成本

10 顆 × 一次 call × 約 4K 輸入 token + 500 輸出 token = 45K total per round

| 模型 | 約略單價 | 一輪費用 |
|---|---|---|
| GPT-4o | $2.5/M input, $10/M output | ~$0.12 |
| Llama 3.1 405B (Foundry serverless) | $5.33/M input, $16/M output | ~$0.22 |
| Mistral Large 2407 (Foundry serverless) | $3/M input, $9/M output | ~$0.13 |

三輪總計約 **$0.5 USD（~NT$15）**，比 V1+V2 七輪本地推理用的電費還便宜。

---

## 六、隱私聲明（給作業報告補一段）

> V2 改用 Azure AI Foundry 託管推理，雖屬雲端服務，
> Azure 企業條款保證輸入內容**不被當訓練資料**、不長期保存（abuse monitoring 預設 30 天 log，可申請關閉）、
> region 鎖在 East US 2 / Sweden Central。對 datasheet 這類**公開但商業敏感**的內容已足夠。
> 採用此方案的目的是建立準確率天花板對照——本地量化模型（qwen2.5:7b 60-62%、14b 64.5%）能達到什麼程度，
> 雲端大模型（GPT-4o、Llama 405B、Mistral Large）能達到什麼程度，差距在哪。

---

## 七、Troubleshooting

| 症狀 | 可能原因 |
|---|---|
| `KeyError: 'AZURE_OPENAI_ENDPOINT'` | `.env` 沒正確讀到，檢查檔名是否真的是 `.env`（不是 `.env.txt`） |
| `401 Unauthorized` | API key 過期或拷錯，去 portal 拿新的 |
| `404 deployment not found` | `AZURE_OPENAI_DEPLOYMENT` 名稱與 portal 上實際 deployment 名稱不一致 |
| Foundry 模型回 `429 rate limit` | Serverless 有 TPM 上限，等一下重試或開 PTU |
| JSON 解析錯誤 | Mistral 偶爾回 markdown fence 包 JSON，main.py 的 `extract_json` 有容錯 |
