# Datasheet 參數提取準確率報告

## 1. 方法說明

- **任務**：從 10 份電子元件 datasheet PDF 自動提取 11 個結構化欄位
- **模型**：Ollama 本地推理 — `qwen2.5:7b` (Q4_K_M 量化, 約 4.7GB)
- **temperature**：0.0（確定性輸出）
- **num_ctx**：16384（context window）
- **PDF 抽取**：pdfplumber（純文字 + 表格）
- **PDF 字元上限**：12000（超過時優先保留含關鍵字頁，避免淹沒 context）

### 為什麼選擇本地部署

- **資料安全**：Datasheet 對部分公司是商業敏感資料，本地推理確保不上雲
- **成本可控**：Ollama 一次安裝後無 API 費用
- **離線運作**：內網 / 工廠環境仍可使用
- **可審計**：所有 prompt、回應、模型權重皆在本機

## 2. 整體準確率

**67 / 110 = 60.9%**

## 3. 各元件準確率

| Part Number | 正確/總數 | 準確率 |
|---|---|---|
| 1N4148W | 9/11 | 81.8% |
| BAS16 | 7/11 | 63.6% |
| BAS21H | 6/11 | 54.5% |
| BAT750 | 8/11 | 72.7% |
| BAV99W | 6/11 | 54.5% |
| CD4148WTP | 8/11 | 72.7% |
| DFLS160 | 7/11 | 63.6% |
| MBR15U150 | 3/11 | 27.3% |
| MSB30M | 7/11 | 63.6% |
| SBR05U20LPS | 6/11 | 54.5% |

## 4. 提取結果總表

| Part | MinT | MaxT | L(mm) | W(mm) | H(mm) | PIN | I_O/I_F(A) | V_F | V_RRM | I_R |
|---|---|---|---|---|---|---|---|---|---|---|
| 1N4148W | -55 | 125 | 3.99 | 1.62 | 1.8 | 2 | 0.15 | 0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150 | 75 | 2.5uA @75V、25nA @20V |
| BAS16 |  | 150 | 2.9 | 1.3 | 1 | 3 | 0.215 | 0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150 | 100 | 30nA @25V,30µA @150V、50µA @150V |
| BAS21H | -55 | 150 | 1.7 | 1.25 | 0.85 | 2 | 0.2 | 1000 @100 mAdc、1250 @200 mAdc |  | 0.1 uA @200 Vdc、100 uA @200 Vdc, TJ = 15 |
| BAT750 | -55 | 125 | 3.0 | 1.4 | 1.15 | 3 | 0.75 | 340 @500mA、390 @750mA、420 @1000mA、475 @1 | 40 | 50uA @30V、175nA @25V |
| BAV99W | -55 | 150 |  |  |  | 3 | 0.15 | 0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150 |  | 30nA @25V、200uA @80V |
| CD4148WTP | -55 | 150 | 1.55 | 0.8 | 0.65 | 2 | 0.1 | 1 @10mA、1.25 @100mA | 75 | 0.025uA @20V、5uA @75V |
| DFLS160 | -65 | 150 |  |  |  | 4 | 1.0 | 0.50 @1.0A | 60 | 0.1 mA @60V,25°C |
| TO-277 | -55 | 150 | 4.1 | 1.9 | 6.6 | 3 | 0.177 | 0.7 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA |  | 10uA @75V |
| MSB30M | -55 | 150 | 6.7 | 8.6 | 1.4 | 4 | 3 | 0.88 @IF = 3.0A, TA = +25°C、1.02 @IF = 3 | 1000 | 500μA @VR = 1,000V, TA = +125°C |
| SBR05U20LPS | -65 | 150 |  |  |  | 2 | 0.5 | 0.31 @0.2A, TJ = +150°C、0.47 @0.5A, TJ = | 20 | 1.5 mA @VR = 20V, TJ = +150°C |

> 註：V_F 與 I_R 因為含多個測試條件，表中只顯示前 40 字元，完整內容見 `results.json`

## 5. 錯誤欄位分析

### 1N4148W (9/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Width (mm)` | `1.8` | `1.62` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Height (mm)` | `1.35` | `1.8` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |

### BAS16 (7/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Minimum Operating Temperature(°C)` | `-65` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Width (mm)` | `2.5` | `1.3` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Height (mm)` | `1.1` | `1` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `I_R(Reverse Current) ` | `'30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V、15...` | `'30nA @25V,30µA @150V、50µA @150V'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |

### BAS21H (6/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Length (mm)` | `2.7` | `1.7` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Width (mm)` | `1.35` | `1.25` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Height (mm)` | `1` | `0.85` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `V_F(Forward Voltage) (V)` | `'1 @100mA、1.25 @200mA'` | `'1000 @100 mAdc、1250 @200 mAdc'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |
| `V_RRM(Peak Repetitive Reverse Voltage) (V)` | `250` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |

### BAT750 (8/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Width (mm)` | `2.55` | `1.4` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `V_F(Forward Voltage) (V)` | `'0.49 @750mA'` | `'340 @500mA、390 @750mA、420 @1000mA、475 @1500mA'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |
| `I_R(Reverse Current) ` | `'100uA @30V'` | `'50uA @30V、175nA @25V'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |

### BAV99W (6/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Minimum Operating Temperature(°C)` | `150` | `-55` | ⚠️ 標答 150 但 datasheet 寫 -55 (Tj/Tstg=-55~+150) |
| `Maximum Length (mm)` | `2.2` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Width (mm)` | `2.2` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Height (mm)` | `1` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `V_RRM(Peak Repetitive Reverse Voltage) (V)` | `150` | `null` | ⚠️ 標答 150 但 datasheet 寫 100 (V_RRM=100V) |

### CD4148WTP (8/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Length (mm)` | `1.65` | `1.55` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Width (mm)` | `0.9` | `0.8` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Height (mm)` | `0.75` | `0.65` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |

### DFLS160 (7/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Length (mm)` | `3.9` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Width (mm)` | `1.93` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Height (mm)` | `1` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `PIN Number` | `2` | `4` | 字串不完全相符 |

### MBR15U150 (3/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Part Number` | `'MBR15U150'` | `'TO-277'` | 字串不完全相符 |
| `Maximum Length (mm)` | `6.6` | `4.1` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Width (mm)` | `4.1` | `1.9` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Height (mm)` | `1.2` | `6.6` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `I_O、I_F (A)` | `15` | `0.177` | 數值偏差超過 ±5% 容差 |
| `V_F(Forward Voltage) (V)` | `'0.84 @15A,25°C、0.73 @15A,125°C'` | `'0.7 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |
| `V_RRM(Peak Repetitive Reverse Voltage) (V)` | `150` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `I_R(Reverse Current) ` | `'10uA @150V,25°C、2mA @150V,125°C'` | `'10uA @75V'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |

### MSB30M (7/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Length (mm)` | `8.6` | `6.7` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Width (mm)` | `6.7` | `8.6` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `Maximum Height (mm)` | `1.5` | `1.4` | 尺寸抓到 NOM/TYP 而非 MAX，或長寬抓反 |
| `V_F(Forward Voltage) (V)` | `'1.1 @3A,25°C'` | `'0.88 @IF = 3.0A, TA = +25°C、1.02 @IF = 3.0A, TA = +125°C'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |

### SBR05U20LPS (6/11)

| 欄位 | 期望 | 提取 | 可能原因 |
|---|---|---|---|
| `Maximum Length (mm)` | `1.075` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Width (mm)` | `0.675` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `Maximum Height (mm)` | `0.4` | `null` | LLM 沒抽到（PDF 中可能該欄位格式特殊） |
| `V_F(Forward Voltage) (V)` | `'0.5 @0.5A,25°C'` | `'0.31 @0.2A, TJ = +150°C、0.47 @0.5A, TJ = +25°C、0.42 @0.5A, ...` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |
| `I_R(Reverse Current) ` | `'50uA @20V,25°C、5mA @20V,150°C'` | `'1.5 mA @VR = 20V, TJ = +150°C'` | 條件 token 命中率 0.0 (<50%)，可能格式或測試條件不齊 |

## 6. 疑似標準答案錯誤

以下欄位在比對時仍以 specbook.xlsx 為準，但 datasheet 內容與標答不一致：

- **BAV99W** / `Minimum Operating Temperature(°C)`：標答 150 但 datasheet 寫 -55 (Tj/Tstg=-55~+150)
- **BAV99W** / `V_RRM(Peak Repetitive Reverse Voltage) (V)`：標答 150 但 datasheet 寫 100 (V_RRM=100V)

## 7. 主要 Limitation

- **尺寸 (Length / Width / Height)**：pdfplumber 對 mechanical drawing 表格的 cell 拆解混亂，LLM 難以分辨哪個欄位是長/寬/高，且常抓到 NOM/TYP 而非 MAX
- **multi-product datasheet**：含多個型號變體的 PDF，7B 量化模型容易把封裝代號當成 Part Number
- **V_F / I_R 條件不齊**：標答列出多個測試條件時，LLM 有時只抽其中一兩個，或抽到的條件格式與標答不完全相同
- **疑似標答錯誤**：BAV99W 兩個欄位的 spec 與 datasheet 明顯不一致，影響該元件的可達天花板
