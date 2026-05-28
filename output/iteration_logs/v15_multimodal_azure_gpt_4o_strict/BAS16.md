# BAS16

_Cell: `v15_multimodal_azure_gpt_4o_strict`  ·  Started: 2026-05-22T12:08:41.333043_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 8 張（頁碼 [1, 2, 3, 4, 5, 6, 8, 9]）
- 耗時: 2991 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21760 字元 + 8 張圖
- Response: 471 字元, 耗時 10799 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 3.0,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.215,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C"
}
```

### Validator
- ⚠️ 1 條 fix:
  - `I_R: '30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C' → '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C'`

### Critic (strict)
- ❌ FAIL, 耗時 18073 ms
- Prompt: 14801 字元, Response: 724 字元
- 6 條 corrections:
  - Minimum Operating Temperature(°C): 現值 '-65' 錯誤，應改為 '-55'，因為應取 Tj (Junction Temperature) 而非 Tstg (Storage Temperature)。
  - Maximum Length (mm): 現值 '3.0' 錯誤，應改為 '2.9'，因為 Package Outline 表中 MAX 值為 2.9 mm。
  - Maximum Width (mm): 現值 '1.4' 錯誤，應改為 '1.3'，因為 Package Outline 表中 MAX 值為 1.3 mm。
  - Maximum Height (mm): 現值 '1.1' 錯誤，應改為 '1.0'，因為 Package Outline 表中 MAX 值為 1.0 mm。
  - I_O、I_F (A): 現值 '0.215' 錯誤，應改為 '0.215 (mA 換算為 A)'，因為 datasheet 中標示為 215 mA，需換算為 0.215 A。
  - I_R(Reverse Current): 現值 '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C' 錯誤，應改為 '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C'，需確認條件完整性，datasheet 中條件無誤。

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 23052 字元 + 8 張圖
- Response: 471 字元, 耗時 10497 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.9,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 1.0,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.215,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 15881 ms
- Prompt: 14801 字元, Response: 813 字元
- 7 條 corrections:
  - Minimum Operating Temperature(°C): 現值 -55，應改為 -65；datasheet 中 Tj (Junction Temperature) 的範圍是 -65 至 150°C。
  - Maximum Operating Temperature(°C): 現值 150，應改為 150；datasheet 中 Tj (Junction Temperature) 的範圍是 -65 至 150°C。
  - Maximum Length (mm): 現值 2.9，應改為 3.0；datasheet 中 Package Outline 圖中標示的最大長度為 3.0 mm。
  - Maximum Width (mm): 現值 1.3，應改為 1.4；datasheet 中 Package Outline 圖中標示的最大寬度為 1.4 mm。
  - Maximum Height (mm): 現值 1.0，應改為 1.1；datasheet 中 Package Outline 圖中標示的最大高度為 1.1 mm。
  - I_O、I_F (A): 現值 0.215，應改為 0.215 A；datasheet 中的值為 215 mA，需轉換為 A。
  - I_R(Reverse Current): 現值 '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C'，應改為 '30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C'；datasheet 中使用的是 µA 而非 uA，需統一為 µA。

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 23136 字元 + 8 張圖
- Response: 471 字元, 耗時 13539 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 3.0,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.215,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C"
}
```

### Validator
- ⚠️ 1 條 fix:
  - `I_R: '30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C' → '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C'`

### Critic (strict)
- ❌ FAIL, 耗時 16582 ms
- Prompt: 14801 字元, Response: 718 字元
- 6 條 corrections:
  - Minimum Operating Temperature(°C): 現值 '-65' 錯誤，應改為 '-55'，因為應取 Tj (Junction Temperature) 而非 Tstg (Storage Temperature)。
  - Maximum Length (mm): 現值 '3.0' 錯誤，應改為 '2.9'，因為 Package Outline 圖中標示的最大值為 2.9 mm。
  - Maximum Width (mm): 現值 '1.4' 錯誤，應改為 '1.3'，因為 Package Outline 圖中標示的最大值為 1.3 mm。
  - Maximum Height (mm): 現值 '1.1' 錯誤，應改為 '1.0'，因為 Package Outline 圖中標示的最大值為 1.0 mm。
  - I_O、I_F (A): 現值 '0.215' 錯誤，應改為 '0.215'（單位需明確標示為 A），datasheet 中標示的最大值為 215 mA。
  - I_R(Reverse Current): 現值 '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C' 錯誤，應改為 '30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C'，因為單位應統一使用 'µA' 而非 'uA' 或 'nA'。

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 88372 ms
- 最終 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 3.0,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.215,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C"
}
```