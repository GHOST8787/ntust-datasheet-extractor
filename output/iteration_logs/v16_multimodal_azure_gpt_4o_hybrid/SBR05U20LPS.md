# SBR05U20LPS

_Cell: `v16_multimodal_azure_gpt_4o_hybrid`  ·  Started: 2026-05-22T12:45:24.342488_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 2567 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21784 字元 + 5 張圖
- Response: 501 字元, 耗時 19147 ms
- 抽到的 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、50uA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 32108 ms
- Prompt: 13546 字元, Response: 298 字元
- 3 條 corrections:
  - Maximum Length (mm): Correct value is 1.075 mm (matches D Max in datasheet).
  - Maximum Width (mm): Correct value is 0.675 mm (matches E Max in datasheet).
  - Maximum Height (mm): Correct value is 0.40 mm (matches A Max in datasheet).

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22694 字元 + 5 張圖
- Response: 501 字元, 耗時 24777 ms
- 抽到的 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、50uA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 25411 ms
- Prompt: 13546 字元, Response: 469 字元
- 3 條 corrections:
  - Maximum Length (mm): The provided value is 1.075 mm, but the datasheet specifies the maximum value for D as 1.075 mm. This is correct.
  - Maximum Width (mm): The provided value is 0.675 mm, but the datasheet specifies the maximum value for E as 0.675 mm. This is correct.
  - Maximum Height (mm): The provided value is 0.4 mm, but the datasheet specifies the maximum value for A as 0.4 mm. This is correct.

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 22865 字元 + 5 張圖
- Response: 501 字元, 耗時 24558 ms
- 抽到的 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "50uA @20V,25°C、5mA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 18118 ms
- Prompt: 13546 字元, Response: 297 字元
- 3 條 corrections:
  - Maximum Length (mm): Correct value is 1.075 mm (matches D Max in datasheet).
  - Maximum Width (mm): Correct value is 0.675 mm (matches E Max in datasheet).
  - Maximum Height (mm): Correct value is 0.40 mm (matches A Max in datasheet).

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 146698 ms
- 最終 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "50uA @20V,25°C、5mA @20V,150°C"
}
```