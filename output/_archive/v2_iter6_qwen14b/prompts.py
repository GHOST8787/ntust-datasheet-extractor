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

### 步驟 2：JEDEC 維度標籤對應

- **D = 長度方向**(Length)
- **E = 寬度方向**(Width)
- **A = 高度方向**(Height / Thickness)

注意有些 datasheet 用 X/Y/Z 或廠商自訂(L1/W1/H 等)，要從圖示判斷。

### 步驟 3：取 MAX 欄

Package Outline 表通常有 4 欄：Symbol / MIN / NOM (or TYP) / MAX。
**只取 MAX 那一欄**。若只給 NOM/TYP 沒給 MAX，填 NOM/TYP 的值(次優)。

### 步驟 4：單位換算

若表頭單位是 `inches`，每個值乘以 **25.4** 換成 mm。

### 步驟 5：sanity check

Surface mount 二極體封裝的 body 尺寸經驗範圍：
- 長度 D：0.8 ~ 10 mm
- 寬度 E：0.5 ~ 8 mm
- 高度 A：0.3 ~ 4 mm

**若抽到的值明顯超出此範圍，幾乎可確認抓錯表(可能抓到 footprint 或 lead spread)，回頭重看**。

### 範例

✓ 表頭「Package Outline Dimensions」+ Symbol=D 列 MAX 欄=2.85mm → Length=`2.85`
✓ 表頭單位 inches，D MAX=0.075 → Length=`0.075 × 25.4 = 1.905`
✗ 表頭「Recommended Land Pattern」的尺寸 — 那是焊墊不是 body
✗ 抓到 lead-to-lead 跨距(腳間距，常 > body 長度)
✗ 抓到 NOM / TYP 而不是 MAX 欄

三個維度若 datasheet 只給兩個，缺的填 `null`(不要猜)。

## 7. PIN Number — 整數
- **封裝實體針腳數**，先看封裝代號比對：

| 封裝類別 | PIN |
|---|---|
| SOD-123 / SOD-323 / SOD-523 / DO-214 (SMA/SMB) / DO-41 / MELF (DO-213) | 2 |
| SOT-23 / SOT-323 / SOT-353 | 3 |
| 單相橋式整流封裝(4 端子標準包) | 4 |
| SO-8 / SOIC-8 | 8 |

- ✓ 任一 dual-diode(共陽/共陰)在 SOT-23 → 3
- ✓ 任一 single-phase bridge rectifier → 4
- ✓ 單顆 single diode 在 SOT-23 封裝(只用 2 隻腳，第 3 腳 NC)→ 仍以**實體腳數**為準
- ✗ 看到 SOT-23 就一律 3 — 先確認元件功能與接腳定義

## 8. I_O、I_F (A) — 浮點
- Average Rectified Output Current (I_O) 或 Forward Continuous Current (I_F)
- **單位一律 A**，mA 必須 ÷1000
- ✓ datasheet 寫 "I_F = <N> mA" → 填 `<N>/1000`(範例：`<N>=200` → `0.2`)
- ✓ datasheet 寫 "I_O = <M> A" → 填 `<M>`(已是 A 單位)
- ✗ 看到 "I_F = <N> mA" 直接填 `<N>` — mA 沒換算

## 9. V_F(Forward Voltage) (V) — 字串
- 列出 Electrical Characteristics 表中**所有測試條件**(datasheet 列幾個就抽幾個)
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
