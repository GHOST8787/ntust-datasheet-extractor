"""V2 prompt 模板 — 單段式 unified prompt(iter 3 版本)

歷史:
  iter 0: baseline 含具體範例值
  iter 1: 範例值改 placeholder + 加防污染警示
  iter 2: L/W/H 規則加 chain-of-thought + 修 V_F 過嚴的副作用
  iter 3: 加 validators.py 後處理(prompt 與 iter 2 相同)
  → 此版本即 iter 3 的 prompt 狀態，搭配 validators.py 為最佳組合
"""

PROMPT_TEMPLATE = """你是專業的電子元件 datasheet 參數提取專家。

# 任務
從下方 datasheet 純文字中，**只針對指定型號**抽出 11 個結構化欄位，
回覆**純 JSON**，不附任何說明文字。

# 指定型號
Part Number: {PART_NUMBER}

> ⚠️ 若 datasheet 含多個型號或封裝變體，**只抽 {PART_NUMBER} 的資料**。
>   不要被其他型號、封裝代號、或廠商後綴(例如尾端 "T1-D"、"-7-F")干擾。

---

# ⚠️ 重要：範例值規則(必讀)

下方所有規則中，含 `<...>` 的是**格式占位符**，
含具體數值的範例(如 `<X>`、`<v1>`)只示意**格式結構**，
**禁止把範例值當答案輸出** — 真實值必須從 datasheet 內容抽取。
若 datasheet 沒給某欄位，填 `null`，**絕對不要編造或抄範例**。

---

# 輸出 JSON Schema(11 個 key 必須全部出現)

{{
  "Part Number": str,
  "Minimum Operating Temperature(°C)": int | null,
  "Maximum Operating Temperature (°C)": int | null,
  "Maximum Length (mm)": float | null,
  "Maximum Width (mm)": float | null,
  "Maximum Height (mm)": float | null,
  "PIN Number": int | null,
  "I_O、I_F (A)": float | null,
  "V_F(Forward Voltage) (V)": str | null,
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": int | null,
  "I_R(Reverse Current) ": str | null
}}

> Key 特殊字元一字不漏：`°C`、全形頓號 `、`、
> `Maximum Operating Temperature (°C)` 在 ( 前有 1 個空白、
> `I_R(Reverse Current) ` 尾端有 1 個空白。

---

# 各欄位規則(每欄含 ✓ 對例 / ✗ 反例)

## 1. Part Number
- 直接填 `{PART_NUMBER}`，不用從 datasheet 解析
- ✗ 不要填封裝代號或含 revision 字尾

## 2. Minimum Operating Temperature(°C) — 整數
- 抓 **Tj(Junction Temperature)** 或 **T_op** 的下限
- ✓ datasheet 句型 "Tj = <lo> to <hi>°C" → 填 `<lo>`(通常為負整數)
- ✗ 用 Tstg(Storage Temperature)的值 — 那是儲存不是運行
- 若 datasheet 把 Tj 與 Tstg 併寫成 "Tj/Tstg = a to b"，視為 Tj 範圍
- **特殊 fallback**：若 datasheet 只給 **Tj 單一值**（例 `Tj = 150°C max`）且沒明示 Min Operating Temp，則 Min 填 **Tj 的單一值**（規格上限即下限的特殊定義）

## 3. Maximum Operating Temperature (°C) — 整數
- 同上抓 Tj/T_op 的上限 `<hi>`(通常為正整數)

## 4-6. Maximum Length / Width / Height (mm) — 浮點

### 步驟 1：先區分三種尺寸表格(只能用第一種)

datasheet 通常會出現這三類「尺寸」表，**只能用 A**：

| 表類型 | 內容 | 是否使用 |
|---|---|---|
| **A. Package Outline / Body Dimensions / Mechanical Drawing** | 晶片實體封裝的長寬高 | ✅ 用這個 |
| B. Recommended Land Pattern / Solder Pad Layout / Footprint | PCB 焊墊建議尺寸(通常比 body 大) | ❌ 不要用 |
| C. Tape and Reel / Pocket Dimensions / Marking | 包裝或印標尺寸 | ❌ 不要用 |

判斷依據：表格標題或前後文是否含 "Outline"、"Mechanical"、"Body"。
含 "Land Pattern"、"Footprint"、"Recommended"、"Tape"、"Reel" 一律不用。

### 步驟 2：JEDEC 維度標籤對應（含 Lead-Body Disambiguation）

- **D = 長度方向**(Length)，本體不含引腳
- **E = 寬度方向**(Width)，本體不含引腳
- **A = 高度方向**(Height / Thickness)
- **H_E 或 H** = **含引腳總寬度**（lead-to-lead span，比 E 大）
- **D2 / E1** = 散熱片或變體尺寸

⚠️ **取 body 尺寸用 E，不能用 H_E**（H_E 是含引腳跨距，不是 body 寬度）。
若 datasheet 同時列 E 跟 H_E：W = E Max，不是 H_E Max。
若只列 H 沒列 E：可能是某些封裝（TO-220 等）H 就是含引腳總寬 → 用其他標註判斷。

注意有些 datasheet 用 X/Y/Z 或廠商自訂(L1/W1/H 等)，要從圖示判斷。

### 步驟 2.5：符號對應是硬性規則，**禁止用「視覺長度」覆蓋**

⚠️ datasheet 內的尺寸符號 D/E/A 是硬性對應到欄位，**不論物理上哪個方向「比較長」**：

- **D Max → Maximum Length (mm)**（即使 D 比 E 小）
- **E Max → Maximum Width (mm)**（即使 E 比 D 大）
- **A Max → Maximum Height (mm)**

**某些封裝 W > L 是正常的**，常見案例：
- **DPAK / TO-252**：D ≈ 6.22, E ≈ 6.73（W > L）
- **D2PAK / TO-263**：D ≈ 9.65, E ≈ 10.67（W > L）
- 任何含 thermal pad 的封裝都可能 E > D

✓ 看到 DPAK datasheet 表內 D Max=6.22, E Max=6.73 → 填 L=6.22, W=6.73（不要因為「6.73 視覺上比較長」就把它填 L）
✗ 禁止用「視覺上哪個方向比較長」推翻 D/E 符號對應
✗ 禁止用「L 必須 ≥ W 常識」推翻 D/E 符號對應

**L/W/H 只能用 A/D/E 三個符號的 Max 值，禁止用 D2/E2/L/L1/H/H_E 等變體填 L/W/H**。

### 步驟 2.6：截圖含多個圖時的選擇規則

若截圖內同時包含：
- **Package Outline / Body Dimensions 表**（含 A/D/E Symbol + Min/Nom/Max 欄）→ **必須用這個**
- **Recommended Land Pattern / Solder Pad 圖**（含 5.55 / 6.5 / 2.85 等焊墊跨度數字）→ **禁止填入 L/W/H**

兩個都在同一頁時，**只用 Package Outline 表內的 A/D/E Max 欄**。Land Pattern 圖內的數字（即使單位是 mm）禁止當作 body 尺寸填。

### 步驟 3：取 MAX 欄（不是 Min / 不是 Nom）

Package Outline 表通常有 4 欄：**Symbol | MIN | NOM (or TYP) | MAX**。

⚠️ **嚴格規則**：取**最右邊那欄（MAX）**的值。

✗ **禁止取 MIN 欄**（最左邊那欄）。
✗ **禁止取 NOM / TYP 欄**（中間那欄）。
✓ 只取 **MAX**（最右邊那欄）。

範例（FFSH5065B 表內 A 列）：
```
DIM  | MIN  | NOM  | MAX
A    | 4.58 | 4.70 | 4.82
```
✓ Max Height = **4.82**（A 列的 MAX）
✗ 不要填 4.58（A 列的 MIN）
✗ 不要填 4.70（A 列的 NOM）

若只給 NOM/TYP 沒給 MAX，填 NOM/TYP 的值(次優)。但**只要 MAX 欄有值就用 MAX**。

### 步驟 3.5：禁用變體符號當 L/W/H

✗ **L/W/H 只能用 A/D/E 三個符號的值，禁止用以下變體**：
- **A1, A2** = 引腳厚度 / 引腳長度（不是 Height）
- **E1, E2** = 變體寬度 / 散熱片寬度（不是 Width）
- **D1, D2** = 變體長度 / 散熱片長度（不是 Length）
- **L, L1** = **lead length（引腳長度），不是 body Length**（L 容易讓人誤填 Maximum Length）
- **H, H1, H_E** = 含引腳總高/總寬（不是 body Height/Width）
- **b, b1, b2, b3, c, c1** = 引腳寬度厚度（不是 L/W/H）
- **e, e1** = 引腳間距 pitch（不是 L/W/H）
- **Q, S, P** = 其他輔助尺寸

✓ **僅以 A Max / D Max / E Max 填 Maximum Height / Length / Width**。

### 步驟 3.6：對應總檢查（最關鍵，防 LLM 搞混 D vs E）

**永恆規則**：
- `D` → `Maximum Length`（**永遠**，不論 D vs E 哪個大）
- `E` → `Maximum Width`（**永遠**，不論 D vs E 哪個大）
- `A` → `Maximum Height`（**永遠**）

**完整範例（用實際 datasheet 數字示範）**：

✓ **範例 1（TO-247 大封裝, D > E）**：
   表內 D Max=20.82, E Max=15.87, A Max=4.82, E2 Max=5.20
   → **L=20.82**（取 D Max）, **W=15.87**（取 E Max）, **H=4.82**（取 A Max）

✓ **範例 2（DPAK, E > D 反直覺）**：
   表內 D Max=6.22, E Max=6.73, A Max=2.39
   → **L=6.22**（取 D Max）, **W=6.73**（取 E Max）, **H=2.39**（取 A Max）
   ⚠️ 即使 W > L，仍按符號對應，不要交換

✓ **範例 3（D2PAK, A Min/Max 都列）**：
   表內 A Min=4.06, A Nom=4.45, A Max=4.83
   → **H=4.83**（取 A 的 MAX 欄，不是 A 的 MIN 欄 4.06，也不是 NOM 4.45）

✗ **反例 1**：表內 D Max=20.82, E Max=15.87 → L=15.87, W=20.82
   錯誤：D 跟 E 對應交換了。**永遠 L=D / W=E**

✗ **反例 2**：表內 D Max=20.82, E2 Max=5.20 → W=5.20
   錯誤：把 E2 變體當 W，應該用 E Max=15.87

✗ **反例 3**：表內 A Min=4.06, A Max=4.83 → H=4.06
   錯誤：取了 MIN 欄，永遠取 MAX 欄

✗ **反例 4**：表內 D Max=15.25, L Max=14.02 → L=14.02
   錯誤：把 L（lead length）當 body Length，應該用 D Max=15.25

### 步驟 4：單位換算

若表頭單位是 `inches`，每個值乘以 **25.4** 換成 mm。

### 步驟 5：sanity check（不靠經驗，靠圖）

**禁止用「合理範圍」經驗判斷尺寸**。元件封裝從 SOD-123（D ~ 2mm）到 TO-247（D ~ 21mm）尺寸落差極大，任何「常見範圍」的假設都會 fail。

正確做法：
- 對照截圖內的尺寸**標註方向**：D 通常是水平標註（長度）/ E 通常是垂直標註（寬度）/ A 通常是側視圖高度
- 以截圖實際標註的 Max 欄數值為準，**不論大小**
- 矩形封裝（DPAK / TO-247 等）通常 L > W（長 > 寬）；若抽到 L < W 要回頭核對方向

### 步驟 6：焊盤反推 body（沒 Package Outline 時的物理推理）

當 datasheet **只給 Recommended Land Pattern / Footprint，沒給 Package Outline / Body Dimensions** 時：

- **零件實體（含引腳）總長度 ≈ 焊盤總跨度 × 80~95%**
- 從焊盤外緣到外緣的跨度反推 body 尺寸
- 焊盤跨度通常 ≥ body 尺寸 5~20%（焊盤要比 lead 大一點才能焊）

範例：
- 焊盤總跨度 L = 2.0mm → 估 body L ≈ 1.6~1.9mm（取中段 ~1.7mm）
- 焊盤總跨度 W = 1.0mm → 估 body W ≈ 0.8~0.95mm

此規則僅在「找不到 Package Outline 表」時觸發，找得到時優先用表內 Max 欄。

### 範例

✓ 表頭「Package Outline Dimensions」+ Symbol=D 列 MAX 欄=2.85mm → Length=`2.85`
✓ 表頭單位 inches，D MAX=0.075 → Length=`0.075 × 25.4 = 1.905`
✗ 表頭「Recommended Land Pattern」的尺寸 — 那是焊墊不是 body
✗ 抓到 lead-to-lead 跨距(腳間距，常 > body 長度)
✗ 抓到 NOM / TYP 而不是 MAX 欄

三個維度若 datasheet 只給兩個，缺的填 `null`(不要猜)。

## 7. PIN Number — 整數
- **封裝實體針腳數**，**優先看截圖實際數接腳數**

**常見封裝參考（fallback 用，看得到圖時以圖為準）**：

| 封裝類別 | PIN |
|---|---|
| SOD-123 / SOD-323 / SOD-523 / DO-214 (SMA/SMB) / DO-41 / MELF (DO-213) | 2 |
| TO-247-2L / TO-220-2L / DPAK-2L | 2 |
| SOT-23 / SOT-323 / SOT-353 | 3 |
| TO-247-3L / TO-220-3L / DPAK-3L | 3 |
| 單相橋式整流封裝(4 端子標準包) | 4 |
| SO-8 / SOIC-8 | 8 |
| SO-14 / SOIC-14 | 14 |
| SO-16 / SOIC-16 | 16 |

通則：
- ✓ 任一 dual-diode(共陽/共陰)在 SOT-23 → 3
- ✓ 任一 single-phase bridge rectifier → 4
- ✓ 單顆 single diode 在 SOT-23 封裝(只用 2 隻腳，第 3 腳 NC)→ 仍以**實體腳數**為準
- ✗ 看到 SOT-23 就一律 3 — 先確認元件功能與接腳定義
- ✗ 沒列的封裝（QFN/QFP/BGA 等）→ 看圖數實際腳數，不要猜

## 8. I_O、I_F (A) — 浮點
- Average Rectified Output Current (I_O) 或 Forward Continuous Current (I_F)
- **單位一律 A**，mA 必須 ÷1000
- ✓ datasheet 寫 "I_F = <N> mA" → 填 `<N>/1000`(範例：`<N>=200` → `0.2`)
- ✓ datasheet 寫 "I_O = <M> A" → 填 `<M>`(已是 A 單位)
- ✗ 看到 "I_F = <N> mA" 直接填 `<N>` — mA 沒換算

## 9. V_F(Forward Voltage) (V) — 字串
- 列出 Electrical Characteristics 表中**所有測試條件**
- **值欄優先取 Max**（跟 L/W/H 一樣的規則）
- **若該條件只有 Typ 沒 Max → 仍要列出該條件**（用 Typ 值充當，**不要跳過**）
- 格式：`值 @條件、值 @條件`，**全形頓號 `、` 分隔**
- 條件最簡寫：`@<I>mA`、`@<I>mA,<T>°C`(去 dc/ac/pk 後綴與變數名)
- **單位一律 V**，mV 必須 ÷1000

**抽取原則(很重要)**：
- datasheet 表中 V_F 那幾列，**有幾個 typical/max 條件就抽幾個**
- 不要漏(缺條件會扣分)，不要編造不存在的條件

- ✓ 格式範例(**值僅占位**)：`"<v1> @<I1>mA、<v2> @<I2>mA"`
- ✓ datasheet 寫 "V_F = <X> mV @ I_F = <Y> mA" → `"<X>/1000 @<Y>mA"`
   例：寫 "715 mV @ 1 mA" → `"0.715 @1mA"`
- ✗ 條件囉嗦含後綴：`"<v> @V_F=<X>V, I_F=<Y> mAdc, T_A=+25°C"`
- ✗ "<X> mV @<Y>mA" 沒做 mV→V 換算
- ✗ 把測試條件中的 V_F=<X>V 抄回值欄(條件內的 V 不是輸出值)

## 10. V_RRM(Peak Repetitive Reverse Voltage) (V) — 整數
- **鎖定 V_RRM**，不要拿 V_R / V_RWM
- 別名清單：`V_RRM` = `Maximum Repetitive Peak Reverse Voltage`
            = `Working Peak Reverse Voltage`
- ✓ datasheet 寫 "V_RRM = <N> V" → 填 `<N>`
- ✗ 拿 V_R(DC blocking voltage)的值 — 那是 DC 不是 peak repetitive

## 11. I_R(Reverse Current) — 字串(注意 key 尾有 1 個空白)
- 列出**所有測試條件**(不同 V_R、不同溫度都要)
- **值欄優先取 Max**（跟 V_F 一樣）
- **若該條件只有 Typ 沒 Max → 仍要列出該條件**（用 Typ 值充當，**不要跳過**）
- 格式：`值單位 @V電壓、值單位 @V電壓,溫度°C`
- **單位必須帶**(uA / nA / mA)；用 `uA` 不用 `μA` 不用 `µA`
- ✓ 格式範例(**值僅占位**)：`"<v1>uA @<VR1>V、<v2>nA @<VR2>V、<v3>uA @<VR3>V,<T>°C"`
- ✗ 沒帶單位：`"<v> @<VR>V"`(看不出是 uA/nA/mA)
- ✗ 條件囉嗦含 Vdc 後綴：`"<v> @V_R=<VR> Vdc"`
- ✗ datasheet 列 25°C 與 150°C 兩條件，只抽 25°C 那條

---

# 輸出規則

1. **只**輸出 JSON 物件，前後不要任何文字、不要 markdown code fence
2. 數值欄位用純數字(不加引號)，字串欄位加雙引號
3. datasheet 沒寫的欄位填 `null`，**不要省 key、不要抄範例值**
4. JSON key 必須與 schema 完全一致(含特殊字元、空白)

# 自我檢查(產 JSON 前自己跑一次)

1. 11 個 key 都齊了？特殊字元(°C、全形頓號、尾端空白)對嗎？
2. 單位都換算好了？(mA→A、mV→V、inch→mm、μ→u)
3. V_F 和 I_R 把所有測試條件都列了？條件數與 datasheet 一致(不超抽不漏抽)？
4. 取的是 Tj 不是 Tstg？
5. L/W/H 取的是 MAX 欄不是 NOM/TYP 欄？
6. V_RRM 鎖定的是 V_RRM 不是 V_R / V_RWM？
7. **任何欄位 datasheet 沒給就填 null，沒抄範例值？**
8. Part Number 直接填 `{PART_NUMBER}` 沒被封裝代號污染？

---

--- 以下是 datasheet 內容 ---

{PDF_TEXT}

--- 以上是 datasheet 內容 ---

請輸出 JSON："""


def build_extraction_prompt(part_number: str, pdf_text: str) -> str:
    """組合 prompt：填入指定型號 + datasheet 純文字"""
    return PROMPT_TEMPLATE.format(PART_NUMBER=part_number, PDF_TEXT=pdf_text)


# ===================================================================
# V3 雙 Agent 迭代用：帶 QA Critic 回饋的 prompt
# ===================================================================
FEEDBACK_BLOCK_TEMPLATE = """
# ⚠️ 第 {ROUND} 輪重抽 — 前一輪答案被審查員指出問題

前一輪你抽出的答案：

```json
{PREV_ANSWER}
```

審查員 (QA Critic) 指出下列錯誤，**這一輪務必修正**：

{CORRECTIONS_BULLETS}

請拿 datasheet 內容重新抽，**特別注意上述錯誤項目**，其他正確的欄位保持不變。
按下方標準規則輸出完整 11 個欄位的 JSON。

---

"""


def build_extraction_prompt_with_feedback(
    part_number: str,
    pdf_text: str,
    prev_answer: dict,
    corrections: list,
    round_num: int,
) -> str:
    """V3 第 2+ 輪用：把上一輪答案 + critic 錯誤清單 prepend 到原 prompt 前。

    round_num: 當前是第幾輪（從 2 開始算，因為第 1 輪不用 feedback）
    """
    import json as _json

    answer_str = _json.dumps(prev_answer, ensure_ascii=False, indent=2)
    bullets = "\n".join(f"- {c}" for c in corrections) if corrections else "- (無具體錯誤)"
    feedback_block = FEEDBACK_BLOCK_TEMPLATE.format(
        ROUND=round_num,
        PREV_ANSWER=answer_str,
        CORRECTIONS_BULLETS=bullets,
    )
    base_prompt = PROMPT_TEMPLATE.format(PART_NUMBER=part_number, PDF_TEXT=pdf_text)
    return feedback_block + base_prompt


# ===================================================================
# V4 多模態：開頭加「截圖使用優先順序」段落
# ===================================================================
MULTIMODAL_PREFIX_TEMPLATE = """\
你會收到下方 datasheet 純文字 + 該 PDF 機械尺寸頁的高清截圖（{NUM_IMAGES} 張）。

# 🖼️ 截圖使用優先順序

對於 **Maximum Length / Width / Height (mm)** 三個機械尺寸欄位：

1. **優先從截圖判斷** — 找截圖中的 **Package Outline / Mechanical Drawing / Body Dimensions** 表
2. **對照 JEDEC 符號** — D = Length（長度方向）、E = Width（寬度方向）、A = Height（高度/厚度）
   - 截圖上若有箭頭標示方向 → 優先用箭頭判斷
   - 某些 datasheet 用 X/Y/Z 或廠商自訂（L1/W1/H 等），從圖示判斷
3. **取 MAX 欄** — 不是 NOM / TYP / Typ
4. **截圖比 OCR 純文字準** — 向量圖內的尺寸文字 OCR 經常抓不到或抓錯，**請以截圖為準**
5. **單位** — 截圖內若標 inches，每個值乘以 25.4 換 mm

對於 **溫度、電流、電壓** 等欄位，從純文字抽取即可（截圖內也可能有，可交叉確認）。

對於 **PIN Number**，封裝圖示是最可靠依據（數實際接腳數）。

---

"""


def build_extraction_prompt_multimodal(
    part_number: str, pdf_text: str, num_images: int
) -> str:
    """V4 第 1 輪 multimodal extraction prompt：在原 prompt 前加截圖使用說明"""
    prefix = MULTIMODAL_PREFIX_TEMPLATE.format(NUM_IMAGES=num_images)
    base = PROMPT_TEMPLATE.format(PART_NUMBER=part_number, PDF_TEXT=pdf_text)
    return prefix + base


def build_extraction_prompt_with_feedback_multimodal(
    part_number: str,
    pdf_text: str,
    prev_answer: dict,
    corrections: list,
    round_num: int,
    num_images: int,
) -> str:
    """V4 第 2+ 輪 multimodal：截圖說明 + critic 回饋 + 原 prompt"""
    import json as _json

    answer_str = _json.dumps(prev_answer, ensure_ascii=False, indent=2)
    bullets = "\n".join(f"- {c}" for c in corrections) if corrections else "- (無具體錯誤)"
    feedback_block = FEEDBACK_BLOCK_TEMPLATE.format(
        ROUND=round_num,
        PREV_ANSWER=answer_str,
        CORRECTIONS_BULLETS=bullets,
    )
    prefix = MULTIMODAL_PREFIX_TEMPLATE.format(NUM_IMAGES=num_images)
    base = PROMPT_TEMPLATE.format(PART_NUMBER=part_number, PDF_TEXT=pdf_text)
    return prefix + feedback_block + base


# ===================================================================
# V6 Chain-of-Thought multimodal：強制 LLM 在 JSON 第一個欄位寫「看圖描述」
# ===================================================================
CHAIN_OF_THOUGHT_HEADER = """\
# 🧠 第一步：先看圖描述，再回答（Chain of Thought）

⚠️ **強制要求**：JSON 輸出的第一個欄位必須是 `_image_reasoning`（字串），逐張描述你看到了什麼：

```
"_image_reasoning": "第 1 張圖：看到什麼 (Package Outline / Body Dimensions / Mechanical Drawing 表) | 表內各 symbol 的 MIN/TYP/MAX 值與單位 | 我判斷 D=Length / E=Width / A=Height 的依據（圖示箭頭/標註）| 任何視覺上模糊或不確定的地方。第 2 張圖：... 第 N 張：..."
```

**先寫 `_image_reasoning` 完畢才填其他 11 個標準欄位**。這個欄位是「思考欄位」，不會影響評估，但會強迫你逐張圖仔細看，減少 L/W/H 三欄機械尺寸的錯誤。

範例輸出結構（值僅為示意）：
```
{{
  "_image_reasoning": "第 1 張圖看到一個 Package Outline 表，D MAX=2.85 / E MAX=1.75 / A MAX=1.30，單位 mm。頂視圖顯示 D 是水平方向（圖左到右）= Length，E 是垂直方向（圖上到下）= Width，A 是側視圖高度標註。第 2 張圖是 Recommended Land Pattern 不應取用。第 3 張...",
  "Part Number": "...",
  "Minimum Operating Temperature(°C)": ...,
  ...其他 10 個欄位...
}}
```

完成 `_image_reasoning` 後，繼續往下看「截圖使用優先順序」與「11 個欄位規則」。

---

"""


def build_extraction_prompt_multimodal_cot(
    part_number: str, pdf_text: str, num_images: int
) -> str:
    """V6 第 1 輪 multimodal + CoT：加 _image_reasoning 強制描述"""
    cot = CHAIN_OF_THOUGHT_HEADER
    prefix = MULTIMODAL_PREFIX_TEMPLATE.format(NUM_IMAGES=num_images)
    base = PROMPT_TEMPLATE.format(PART_NUMBER=part_number, PDF_TEXT=pdf_text)
    return cot + prefix + base


def build_extraction_prompt_with_feedback_multimodal_cot(
    part_number: str,
    pdf_text: str,
    prev_answer: dict,
    corrections: list,
    round_num: int,
    num_images: int,
) -> str:
    """V6 第 2+ 輪 multimodal + CoT"""
    import json as _json

    answer_str = _json.dumps(prev_answer, ensure_ascii=False, indent=2)
    bullets = "\n".join(f"- {c}" for c in corrections) if corrections else "- (無具體錯誤)"
    feedback_block = FEEDBACK_BLOCK_TEMPLATE.format(
        ROUND=round_num,
        PREV_ANSWER=answer_str,
        CORRECTIONS_BULLETS=bullets,
    )
    cot = CHAIN_OF_THOUGHT_HEADER
    prefix = MULTIMODAL_PREFIX_TEMPLATE.format(NUM_IMAGES=num_images)
    base = PROMPT_TEMPLATE.format(PART_NUMBER=part_number, PDF_TEXT=pdf_text)
    return cot + prefix + feedback_block + base
