# V7 M — GPT-4.1-mini Deployment 開設指南

要跑 V7 M（imlacha 用的同顆模型），你需要在 Azure AI Foundry 開新部署。我已經先把 backend code 寫好了，只等你開 deployment + 更新 .env。

## 步驟

### 1. 開 Azure AI Foundry deployment

1. 開瀏覽器到 <https://ai.azure.com>
2. 進你的 project（跟現有 GPT-4o / Llama / Mistral 同一個 project）
3. 左側 Sidebar → **Models + endpoints** → **+ Deploy model**
4. 搜 `gpt-4.1-mini`（**注意**：不是 `gpt-4o-mini`，是 `gpt-4.1-mini`）
5. 選 standard deployment、設 deployment name 為 `gpt-4.1-mini`（簡單好記）
6. Confirm

> 如果搜不到 `gpt-4.1-mini`，可能在你的 region 還沒上架。可改試 `gpt-4o-mini` 當代替（雖然不是 imlacha 用的同顆，但比 GPT-4o 便宜，也能對照）。

### 2. 更新 .env

在 `C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業\.env` 加一行：

```
AZURE_GPT41MINI_DEPLOYMENT=gpt-4.1-mini
```

（值 = 你 deployment name；如果你叫它別的名字，就填那個名字）

### 3. 跟我說「deployment 開好了」

我就會跑 V7 M cell：

```
BACKEND=azure_gpt41mini
CRITIC_PROMPT_MODE=conservative
PDF_EXTRACTOR=multimodal
USE_STRICT_SCHEMA=0
USE_CHAIN_OF_THOUGHT=0
```

= 完全等於 V4 E 的配置但換模型。對照 V4 E (79.1%) 看換模型有沒有改善。

預估成本：~0.5 USD（mini 比 4o 便宜 8 倍）。

## 為什麼這個實驗值得做

- imlacha 用 GPT-4.1-mini 拿 97% — 是他完整方案的關鍵變因之一
- 我們連續 V5/V6 加機制都退步 → 強烈訊號表示 GPT-4o 在 V4 配置下已到天花板
- 換模型 = 完全不同維度，可能突破 79.1% 天花板
- 也可能不會（模型不是真正原因），但只跑 1 cell ~5 分鐘 ~0.5 USD，值得測

## 風險 / 預期

| 結果 | 表示什麼 |
|---|---|
| > 80%（提升）| GPT-4.1-mini 在此任務確實比 GPT-4o 適合 → 模型選擇是關鍵 |
| 75-80%（持平 ±）| 模型選擇不是關鍵；imlacha 的 97% 來自其他因素 |
| < 75%（退步）| 4.1-mini 對 vision / 抽取較弱 → GPT-4o 才是對的 |
