# MSB30M

_Cell: `v11_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T11:39:55.155995_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 3406 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 20870 字元 + 5 張圖
- Response: 448 字元, 耗時 11392 ms
- 抽到的 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 6.7,
  "Maximum Width (mm)": 7.4,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @1.5A,25°C、0.88 @1.5A,125°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1176 ms
- Prompt: 14021 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 15978 ms
- 最終 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 6.7,
  "Maximum Width (mm)": 7.4,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @1.5A,25°C、0.88 @1.5A,125°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```