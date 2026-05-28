# MSB30M

_Cell: `v4_multimodal_azure_mistral_medium_2505_conservative`  ·  Started: 2026-05-22T10:07:14.715730_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [1, 2, 3]）
- 耗時: 2867 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 17847 字元 + 3 張圖
- Response: 464 字元, 耗時 20965 ms
- 抽到的 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 7.4,
  "Maximum Width (mm)": 6.7,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "0.8 @1.5A,25°C、0.88 @1.5A,125°C、1.02 @3.0A,25°C、1.1 @3.0A,125°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1728 ms
- Prompt: 14037 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 25563 ms
- 最終 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 7.4,
  "Maximum Width (mm)": 6.7,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "0.8 @1.5A,25°C、0.88 @1.5A,125°C、1.02 @3.0A,25°C、1.1 @3.0A,125°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```