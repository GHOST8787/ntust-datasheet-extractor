"""快速測試 Azure backend 連線"""
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

from llm_backend import get_backend

for name in ["azure_gpt4o", "azure_llama", "azure_mistral"]:
    print(f"\n=== Testing {name} ===")
    try:
        b = get_backend(name)
        print(f"  Backend: {b.name}")
        print(f"  Archive tag: {b.archive_tag}")
        print(f"  Sending: 'Reply only with: {{\"ok\": true}}'")
        resp = b.call('Reply only with this exact JSON: {"ok": true}', timeout=60)
        print(f"  Response: {resp[:200]!r}")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
