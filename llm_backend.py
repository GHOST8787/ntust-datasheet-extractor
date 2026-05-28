"""LLM backend 抽象層

支援:
  - ollama         : 本地 Ollama(qwen 等)
  - azure_gpt4o    : Azure OpenAI 上的 GPT-4o
  - azure_llama    : Azure AI Foundry serverless 的 Llama 3.1 405B
  - azure_mistral  : Azure AI Foundry serverless 的 Mistral Large

由環境變數 BACKEND 選擇,所有 endpoint / key 從 .env 讀。
"""
import os
from abc import ABC, abstractmethod
from typing import List, Optional

import requests


# ===================================================================
# 抽象介面
# ===================================================================
class LLMBackend(ABC):
    name: str = "abstract"
    archive_tag: str = "abstract"

    @abstractmethod
    def call(self, prompt: str, timeout: int = 600) -> str:
        """送 prompt,回傳 LLM 原始字串(JSON 字串)"""
        ...

    def call_multimodal(
        self, prompt_text: str, base64_images: List[str], timeout: int = 600
    ) -> str:
        """V4 多模態呼叫，預設不支援。Vision-capable backend override 它。"""
        raise NotImplementedError(
            f"{self.name} does not support multimodal calls. "
            f"Use a vision-capable backend (e.g. azure_gpt4o)."
        )


# ===================================================================
# 1. Ollama 本地
# ===================================================================
class OllamaBackend(LLMBackend):
    def __init__(self, model: Optional[str] = None):
        self.url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.model = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:14b")
        self.num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0"))
        self.name = f"ollama:{self.model}"
        # 把 model 名稱轉成檔名安全的 tag(qwen2.5:14b → qwen2_5_14b)
        safe = self.model.replace(":", "_").replace(".", "_").replace("/", "_")
        self.archive_tag = f"ollama_{safe}"

    def call(self, prompt: str, timeout: int = 600) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
            },
        }
        resp = requests.post(self.url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "")


# ===================================================================
# 2. Azure OpenAI(GPT-4o 等)
# ===================================================================
class AzureFoundryV1Backend(LLMBackend):
    """新版 Microsoft Foundry V1 統一 API(OpenAI 相容)。

    同一 project 的所有部署模型共用 endpoint + key,只差 deployment name。
    GPT-4o / Llama / Mistral 都走這條。

    .env 必須設:
      AZURE_FOUNDRY_ENDPOINT = base URL,例如
        https://xxx.services.ai.azure.com/api/projects/yyy/openai/v1
      AZURE_FOUNDRY_KEY      = project key
    再加每個模型自己的 deployment name 環境變數,例如
      AZURE_GPT4O_DEPLOYMENT, AZURE_LLAMA_DEPLOYMENT, AZURE_MISTRAL_DEPLOYMENT
    """

    def __init__(self, deployment: str, archive_tag: str):
        from openai import OpenAI
        endpoint = os.environ["AZURE_FOUNDRY_ENDPOINT"].rstrip("/")
        # 自動修剪常見尾端路徑
        for suffix in ("/responses", "/chat/completions", "/completions"):
            if endpoint.endswith(suffix):
                endpoint = endpoint[: -len(suffix)]
                break
        api_key = os.environ["AZURE_FOUNDRY_KEY"]
        self.deployment = deployment
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0"))
        self.client = OpenAI(
            base_url=endpoint,
            api_key=api_key,
        )
        self.name = f"azure_foundry:{self.deployment}"
        self.archive_tag = archive_tag

    def call(self, prompt: str, timeout: int = 600, response_format: dict = None) -> str:
        """V5 加 response_format 參數 — None 預設 json_object（V3/V4 行為）；
        傳 dict（例如 OPENAI_RESPONSE_FORMAT_STRICT）時用 strict schema mode。
        """
        if response_format is None:
            response_format = {"type": "json_object"}
        resp = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
            temperature=self.temperature,
            timeout=timeout,
        )
        return resp.choices[0].message.content or ""

    def call_multimodal(
        self,
        prompt_text: str,
        base64_images: List[str],
        timeout: int = 600,
        response_format: dict = None,
    ) -> str:
        """V4 多模態呼叫：把文字 + 圖以 OpenAI content blocks 格式送出。
        V5 加 response_format 參數 — None 預設 json_object，dict 走 strict schema。

        只在 vision-capable 部署上 work（如 GPT-4o）。Llama / Mistral 雖然走同 SDK 但部署本身不支援 image_url block，API 會回錯。
        """
        if response_format is None:
            response_format = {"type": "json_object"}
        content = [{"type": "text", "text": prompt_text}]
        for b64 in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64}",
                    "detail": "high",  # 高解析度,讀機械尺寸圖比較準
                },
            })
        resp = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": content}],
            response_format=response_format,
            temperature=self.temperature,
            timeout=timeout,
        )
        return resp.choices[0].message.content or ""


# 舊版相容別名(萬一 .env 還在用 AZURE_OPENAI_*)
AzureOpenAIBackend = AzureFoundryV1Backend


# ===================================================================
# 3. Azure AI Foundry serverless(Llama / Mistral 等開源模型)
# ===================================================================
class AzureFoundryBackend(LLMBackend):
    def __init__(self, endpoint_env: str, key_env: str, archive_tag: str):
        from azure.ai.inference import ChatCompletionsClient
        from azure.core.credentials import AzureKeyCredential
        endpoint = os.environ[endpoint_env]
        key = os.environ[key_env]
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0"))
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        self.name = f"azure_foundry:{archive_tag}"
        self.archive_tag = archive_tag

    def call(self, prompt: str, timeout: int = 600) -> str:
        # azure-ai-inference 的 response_format 用字串 "json_object"
        resp = self.client.complete(
            messages=[{"role": "user", "content": prompt}],
            response_format="json_object",
            temperature=self.temperature,
            max_tokens=4096,
        )
        return resp.choices[0].message.content or ""


# ===================================================================
# Factory
# ===================================================================
def get_backend(name: Optional[str] = None) -> LLMBackend:
    """
    根據環境變數 BACKEND 或傳入 name 建對應 backend.
    支援值: ollama / azure_gpt4o / azure_llama / azure_mistral
    """
    name = (name or os.environ.get("BACKEND", "ollama")).lower()
    if name == "ollama":
        return OllamaBackend()
    elif name == "azure_gpt4o":
        return AzureFoundryV1Backend(
            deployment=os.environ.get("AZURE_GPT4O_DEPLOYMENT", "gpt-4o"),
            archive_tag="azure_gpt_4o",
        )
    elif name == "azure_gpt41mini":
        # V7 M: imlacha 用的 GPT-4.1-mini，等 Sunny 開 Azure deployment 後使用
        return AzureFoundryV1Backend(
            deployment=os.environ.get("AZURE_GPT41MINI_DEPLOYMENT", "gpt-4.1-mini"),
            archive_tag="azure_gpt_41_mini",
        )
    elif name == "azure_llama":
        return AzureFoundryV1Backend(
            deployment=os.environ.get(
                "AZURE_LLAMA_DEPLOYMENT",
                "Llama-4-Maverick-17B-128E-Instruct-FP8",
            ),
            archive_tag="azure_llama_4_maverick",
        )
    elif name == "azure_mistral":
        deployment = os.environ["AZURE_MISTRAL_DEPLOYMENT"]
        # archive_tag 從 deployment name 衍生(例:mistral-medium-2505 → mistral_medium_2505)
        tag_suffix = deployment.lower().replace("-", "_").replace(".", "_")
        return AzureFoundryV1Backend(
            deployment=deployment,
            archive_tag=f"azure_{tag_suffix}",
        )
    else:
        raise ValueError(
            f"Unknown BACKEND: {name!r}. "
            f"Valid: ollama / azure_gpt4o / azure_gpt41mini / azure_llama / azure_mistral"
        )
