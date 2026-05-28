# BAS16

_Cell: `v16_multimodal_azure_gpt_4o_hybrid`  ·  Started: 2026-05-22T12:27:58.818622_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 8 張（頁碼 [1, 2, 3, 4, 5, 6, 8, 9]）
- 耗時: 3720 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21760 字元 + 8 張圖
- Response: 471 字元, 耗時 15521 ms
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

### Critic (hybrid)
- ❌ FAIL, 耗時 14069 ms
- Prompt: 13510 字元, Response: 362 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 2.9 mm as per the datasheet (Package Outline, Fig. 7).
  - Maximum Width (mm) should be corrected to 1.3 mm as per the datasheet (Package Outline, Fig. 7).
  - Maximum Height (mm) should be corrected to 1.0 mm as per the datasheet (Package Outline, Fig. 7).

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22704 字元 + 8 張圖
- Response: 471 字元, 耗時 16333 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
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

### Critic (hybrid)
- ❌ FAIL, 耗時 13661 ms
- Prompt: 13510 字元, Response: 356 字元
- 3 條 corrections:
  - Maximum Length (mm): Correct value is 2.9 mm (matches datasheet Table 3, Ordering Information).
  - Maximum Width (mm): Correct value is 1.3 mm (matches datasheet Table 3, Ordering Information).
  - Maximum Height (mm): Correct value is 1.0 mm (matches datasheet Table 3, Ordering Information).

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 22698 字元 + 8 張圖
- Response: 471 字元, 耗時 33283 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
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

### Critic (hybrid)
- ❌ FAIL, 耗時 44858 ms
- Prompt: 13510 字元, Response: 383 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 2.8 as per the datasheet (Package Outline: 2.8 mm to 3.0 mm).
  - Maximum Width (mm) should be corrected to 1.2 as per the datasheet (Package Outline: 1.2 mm to 1.4 mm).
  - Maximum Height (mm) should be corrected to 0.9 as per the datasheet (Package Outline: 0.9 mm to 1.1 mm).

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 141457 ms
- 最終 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
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