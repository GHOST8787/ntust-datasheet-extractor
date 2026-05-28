"""V3 QA Critic：第二顆 LLM Agent，審查 Extraction Agent 的初始答案

設計參考 imlacha/spec-sheet-extract V7 的 Dual-Agent Self-Correction 機制：
  - Extraction Agent 先抽 → QA Critic Agent 拿 PDF + 初始答案回頭審
  - is_passed=False 時回傳 corrections list，main.py 把它注入下一輪 extraction prompt
  - 最多 3 輪迭代閉環

這個檔不引入新 LLM backend，沿用 llm_backend.py 的同一 backend 跑 critic（省一份設定）。

兩種 critic prompt 模式（環境變數 CRITIC_PROMPT_MODE 切換）：
  - strict (預設)        : 第一版嚴格 critic，會挑很多細節 — 對 Mistral 過度修正
  - conservative         : 保守版，預設 PASS、列「不算錯清單」、禁止反向修改
"""
import json
import os
import re
from typing import Dict, List, Tuple

import config
from llm_backend import LLMBackend


CRITIC_PROMPT_TEMPLATE = """你是嚴格的電子元件 datasheet 抽取**審查員 (QA Critic)**。

# 任務
有另一個 AI Agent 已經從 datasheet 純文字抽出了 {PART_NUMBER} 的規格 JSON（見下方「初始答案」）。
你的工作是：**拿原始 datasheet 文字回頭驗證每個欄位**，找出明顯抓錯、漏抓、單位錯、拿錯欄、條件不全的問題。

# 輸出 JSON Schema（嚴格遵守，不附說明文字）

{{
  "is_passed": bool,        # true = 所有欄位都驗過沒問題；false = 至少一個欄位需要修正
  "corrections": [str, ...] # is_passed=false 時必須非空；每條描述要具體（哪個欄位、現值是什麼、應該改成什麼、為什麼）
}}

# 審查重點（11 個欄位逐項對照）

## 1. Part Number
- 應與指定型號 `{PART_NUMBER}` 完全一致
- ✗ 不該含封裝代號或廠商後綴（例如 -T1-D、-7-F）

## 2-3. Min / Max Operating Temperature (°C)
- 應取 **Tj (Junction)** 或 **T_op** 的範圍，不能用 **Tstg (Storage)**
- 若答案的數值與 datasheet 內 Tstg 行數值一致 → corrections 標記要改用 Tj
- Tj 通常 -55 到 150；Tstg 通常 -65 到 175。看到 -65 / 175 警覺

## 4-6. Maximum Length / Width / Height (mm)
- 必須來自 **Package Outline / Body Dimensions / Mechanical Drawing** 表
- ✗ 不該來自 Recommended Land Pattern / Footprint / Solder Pad（焊墊比 body 大）
- ✗ 不該來自 Tape and Reel / Pocket Dimensions
- 必須取 **MAX 欄**，不是 NOM / TYP 欄
- 若表頭單位 inches，要乘 25.4
- SMD 二極體合理範圍：D 0.8~10mm / E 0.5~8mm / A 0.3~4mm
- 任何欄位 datasheet 沒給時應為 null，看到「猜的近似值」要標記

## 7. PIN Number
- 看封裝代號判斷：SOD-123/323/523/DO-214/DO-41/MELF=2；SOT-23/323/353=3；橋式整流=4；SO-8/SOIC-8=8
- 不能只看「SOT-23 就一律填 3」，要看實際接腳定義

## 8. I_O、I_F (A)
- 單位必須 **A**（mA 要 ÷1000）
- ✗ 看到 "I_F = 200 mA" 直接填 200（沒換算）

## 9. V_F(Forward Voltage) (V) — 字串
- 必須列出 datasheet **所有** typical/max 測試條件，**不可漏抓**
- 格式：`值 @條件、值 @條件`（全形頓號分隔）
- 單位一律 V（mV ÷ 1000）
- 條件最簡寫：`@<I>mA`、`@<I>mA,<T>°C`（去 dc/ac/pk 後綴與變數名）
- ✗ datasheet 列 3 個條件只抽 1 個 → 漏抓
- ✗ 值 > 10 → 沒做 mV→V 換算（V_F 不可能超過 ~5V）

## 10. V_RRM(Peak Repetitive Reverse Voltage) (V)
- 必須是 V_RRM，不能拿 V_R / V_RWM（DC blocking voltage 不算 peak repetitive）

## 11. I_R(Reverse Current) — 字串
- 必須列出 datasheet **所有** 測試條件（不同 V_R、不同溫度都要）
- 單位必須帶（uA / nA / mA），用 `uA` 不用 `μA` / `µA`
- ✗ 漏抓高溫條件（例如 25°C 與 150°C 兩條件只抽 25°C）

---

# 通則
- 你**只負責找錯**，不負責給出修正後的完整 JSON
- 若初始答案是合理的（即使不完美），就 `is_passed=true`、`corrections=[]`
- 若有 1+ 個欄位明顯抓錯/漏抓 → `is_passed=false`，`corrections` 每條一個欄位的具體錯誤
- corrections 描述要具體到能讓下一輪 extraction 直接改：
  - ✓ "V_F: 現值 '0.715 @1mA' 漏抓 100mA 條件；datasheet Electrical Characteristics 表列了 1mA / 10mA / 100mA 三個條件"
  - ✗ "V_F 不對"（太空泛）
- 不要為了挑錯而挑錯。若值看起來合理且 datasheet 確實這樣寫 → 通過

---

# 指定型號
Part Number: {PART_NUMBER}

# 初始答案（待審查）

```json
{INITIAL_ANSWER}
```

# datasheet 原始內容（從 PDF 抽出的純文字）

--- 以下是 datasheet 內容 ---

{PDF_TEXT}

--- 以上是 datasheet 內容 ---

請輸出 JSON："""


# ===================================================================
# 保守版 critic prompt（V3.1 — 從 mistral 過度修正案例反推而來）
# ===================================================================
CRITIC_PROMPT_TEMPLATE_CONSERVATIVE = """你是「**保守版**」的審查員 (Conservative QA Critic)。

# 核心原則：預設 PASS，反證才挑

⚠️ **重要心態調整**：
- 預設 extraction 的答案是**對的**
- 只有你能在 datasheet 文字**直接找到反證**，才標記 corrections
- **寧可漏掉 5 個錯，也不要錯改 1 個對**
- 如果你不確定 → is_passed=true（讓答案保留原狀）

# 「不算錯」清單（即使你覺得不完美，**禁止標記**）

1. **小數點格式差異**：`6.6` vs `6.60`、`1.0` vs `1.00`、`5` vs `5.0` — 數值完全相等
2. **整數浮點互換**：`-55` vs `-55.0`、`100` vs `100.0`
3. **V_F / I_R 字串條件順序差異**：`"0.7 @1mA、0.85 @10mA"` 與 `"0.85 @10mA、0.7 @1mA"` 視為等效
4. **MIN/MAX 同值**：當 datasheet Min/Typ/Max 都同一值，extraction 取任何一個都對
5. **誤差 ±0.05 內**：例如 0.65 vs 0.67 屬於量測公差範圍，**不算錯**

# 「不能反向修改」清單（**禁止建議**）

❌ **不准 Max → Typ**：原 prompt 規則明確「必須取 Max 欄」，你不能反推用 Typ / NOM
❌ **不准 Tj → Tstg**：必須取 Junction Temperature 不能改成 Storage
❌ **不准 V_RRM → V_R**：V_RRM 是 Peak Repetitive，與 V_R (DC blocking) 不同概念

# 重複偵測（強制停手）

如果你發現自己反覆對同一欄位橫跳，**立即 is_passed=true 不再 push**。判斷不準的事不要硬挑。

# 真正該標 corrections 的情況（**明顯錯**才標）

只有滿足以下任一條件才標：

1. **單位顯然漏換算**：例如 V_F = 715（顯然是 mV 沒換成 V，因為 V_F 不可能 > 5V）
2. **明顯抓錯欄**：尺寸 > Body 合理範圍 1.5 倍以上（明顯抓到 Footprint / Land Pattern）
3. **應有值卻填 null**：datasheet 明確列了某參數但 extraction 漏抓
4. **明顯違反規則**：取了 Typ 而不是 Max（在 MAX 欄有值的情況下）
5. **多測試條件嚴重漏抓**：datasheet 列 3 個 V_F 條件但 extraction 只抽 1 個（漏 ≥ 2 個才算）

# 輸出規則

- **is_passed=true**：合理的答案（即使不完美）一律通過
- **is_passed=false**：必須**精確**指出錯誤 + datasheet 反證 + 應該改成什麼具體值
- **corrections 上限：每次最多 3 條**（最嚴重的 3 個，其他放過）

# 輸出 JSON Schema

{{
  "is_passed": bool,
  "corrections": [str, ...]
}}

---

# 指定型號
Part Number: {PART_NUMBER}

# 初始答案（待審查）

```json
{INITIAL_ANSWER}
```

# datasheet 原始內容

--- 以下是 datasheet 內容 ---

{PDF_TEXT}

--- 以上是 datasheet 內容 ---

請輸出 JSON："""


# ===================================================================
# Hybrid critic（V16）— L/W/H 嚴格、其他欄位保守
# ===================================================================
CRITIC_PROMPT_TEMPLATE_HYBRID = """你是「混合審查員」(Hybrid QA Critic)，對不同欄位採不同嚴格度。

# 核心原則：分區嚴格度

**對「機械尺寸 L/W/H 三欄」**（Maximum Length / Width / Height (mm)）採**嚴格審查**：
- 仔細對照截圖內 Package Outline / Body Dimensions 表
- 任何 L/W/H 跟圖內 A/D/E Max 欄不符 → 立刻 corrections
- 特別驗：是否取了 MIN / NOM 欄而不是 MAX 欄
- 是否把 E2/A1/L1 等變體當 L/W/H

**對其他 8 欄位**（Part Number, Min/Max Temp, PIN, I_O, V_F, V_RRM, I_R）採**保守審查**：
- 預設 PASS，反證才挑
- 不挑小數點格式差異
- 不挑 V_F / I_R 字串條件順序
- 不挑 typ vs max 細節（除非完全是 typ 數值）
- 條件數差 1-2 個不算錯（datasheet 列法可能不同）
- **不能反向修改** Max → Typ

# 「不算錯」清單（所有欄位通用）
1. 小數點格式差異（6.6 vs 6.60）
2. 整數浮點互換
3. 字串條件順序差
4. MIN/MAX 同值情境

# 嚴格的「不能反向修改」清單
❌ 不准 Max → Typ
❌ 不准 Tj → Tstg
❌ 不准 V_RRM → V_R

# 重複偵測（強制停手）
反覆對同一欄位橫跳 → is_passed=true 不再 push

# 輸出規則
- is_passed=true：合理答案一律通過（即使機械尺寸略有差距）
- is_passed=false：必須精確指出錯誤 + datasheet 反證 + 應改成什麼具體值
- corrections 上限：每次最多 3 條

# 輸出 JSON Schema

{{
  "is_passed": bool,
  "corrections": [str, ...]
}}

---

# 指定型號
Part Number: {PART_NUMBER}

# 初始答案（待審查）

```json
{INITIAL_ANSWER}
```

# datasheet 原始內容

--- 以下是 datasheet 內容 ---

{PDF_TEXT}

--- 以上是 datasheet 內容 ---

請輸出 JSON："""


def build_critic_prompt(
    part_number: str,
    pdf_text: str,
    initial_answer: Dict,
    mode: str = "strict",
) -> str:
    """組合 critic prompt：給 Critic Agent 看 PDF + 初始答案

    mode:
      - "strict"       : 第一版嚴格 critic（會挑很多細節 — 容易引發過度修正）
      - "conservative" : 保守版（預設 PASS、列「不算錯清單」、禁止反向修改）
      - "hybrid"       : V16 — L/W/H 嚴格看圖、其他欄位保守
    """
    answer_str = json.dumps(initial_answer, ensure_ascii=False, indent=2)

    if mode == "conservative":
        template = CRITIC_PROMPT_TEMPLATE_CONSERVATIVE
    elif mode == "hybrid":
        template = CRITIC_PROMPT_TEMPLATE_HYBRID
    else:
        template = CRITIC_PROMPT_TEMPLATE

    return template.format(
        PART_NUMBER=part_number,
        INITIAL_ANSWER=answer_str,
        PDF_TEXT=pdf_text,
    )


def get_critic_mode() -> str:
    """從環境變數讀 critic mode，預設 strict"""
    mode = os.environ.get("CRITIC_PROMPT_MODE", "strict").lower()
    if mode not in ("strict", "conservative", "hybrid"):
        return "strict"
    return mode


def _extract_json(text: str) -> Dict:
    """跟 main.py 的 extract_json 同邏輯，但這檔不能 import main 避免循環"""
    text = text.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.lower().startswith("json"):
            text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1 or e <= s:
        raise ValueError(f"No JSON found in critic response: {text[:200]!r}")
    return json.loads(text[s:e + 1])


def call_critic(
    backend: LLMBackend,
    part_number: str,
    pdf_text: str,
    initial_answer: Dict,
    mode: str = None,
    images_b64: list = None,
) -> Tuple[bool, List[str], Dict]:
    """跑 Critic Agent 一輪，回傳 (is_passed, corrections, debug_info)

    V14: 加 images_b64 參數。若 backend 支援 multimodal + 有 images → critic 也看圖
    （這樣 critic 能直接驗 LLM 抽的 L/W/H 跟圖上對不對）。

    debug_info 給 iteration_logger 用。

    mode 為 None 時從環境變數 CRITIC_PROMPT_MODE 讀（預設 strict）。
    """
    import time as _time
    import os as _os

    if mode is None:
        mode = get_critic_mode()

    prompt = build_critic_prompt(part_number, pdf_text, initial_answer, mode=mode)
    debug = {"mode": mode, "prompt_chars": len(prompt), "response_raw": "", "elapsed_ms": 0}

    # V14: 是否走 multimodal critic（看 env var + 有 images）
    use_mm_critic = (
        _os.environ.get("USE_MULTIMODAL_CRITIC", "0").lower() in ("1", "true", "yes")
        and images_b64
        and hasattr(backend, "call_multimodal")
    )

    t0 = _time.time()
    try:
        if use_mm_critic:
            raw = backend.call_multimodal(prompt, images_b64, timeout=config.TIMEOUT)
        else:
            raw = backend.call(prompt, timeout=config.TIMEOUT)
        debug["response_raw"] = raw
        debug["elapsed_ms"] = int((_time.time() - t0) * 1000)
        parsed = _extract_json(raw)
    except Exception as e:
        debug["elapsed_ms"] = int((_time.time() - t0) * 1000)
        # Critic 壞了不擋主流程
        return True, [f"[critic_error] {type(e).__name__}: {e}"], debug

    is_passed = bool(parsed.get("is_passed", True))
    corrections_raw = parsed.get("corrections", [])
    if not isinstance(corrections_raw, list):
        corrections_raw = [str(corrections_raw)]
    corrections = [str(c).strip() for c in corrections_raw if str(c).strip()]

    # 防呆：is_passed=False 但 corrections 空 → 視為通過
    if not is_passed and not corrections:
        return True, [], debug
    # 防呆：is_passed=True 但 corrections 非空 → 還是視為通過（critic 自己矛盾就信寬鬆解）
    if is_passed:
        return True, [], debug

    return False, corrections, debug
