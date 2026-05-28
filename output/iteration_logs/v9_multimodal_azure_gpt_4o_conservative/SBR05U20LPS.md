# SBR05U20LPS

_Cell: `v9_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T11:13:30.691939_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 2611 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 19111 字元 + 5 張圖
- Response: 501 字元, 耗時 14649 ms
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

### Critic (conservative)
- ✅ PASS, 耗時 803 ms
- Prompt: 14079 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 18069 ms
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