# SBR05U20LPS

_Cell: `v4_multimodal_toc_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T10:04:06.031484_

## PDF 抽取
- Extractor: `multimodal_toc`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [1, 2, 3]）
- 耗時: 2415 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 17867 字元 + 3 張圖
- Response: 502 字元, 耗時 12519 ms
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
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.34 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.47 @0.5A,25°C、0.42 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、1.5mA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1129 ms
- Prompt: 14080 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 16067 ms
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
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.34 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.47 @0.5A,25°C、0.42 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、1.5mA @20V,150°C"
}
```