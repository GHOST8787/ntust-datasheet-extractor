# MSB30M

_Cell: `v17_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T12:55:03.535291_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 2843 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 464 字元, 耗時 11423 ms
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
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 992 ms
- Prompt: 14037 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 15262 ms
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
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```