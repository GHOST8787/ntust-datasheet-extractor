# DFLS160

_Cell: `v4_multimodal_toc_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T10:01:53.140447_

## PDF 抽取
- Extractor: `multimodal_toc`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [1, 2, 3]）
- 耗時: 2429 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 17851 字元 + 3 張圖
- Response: 392 字元, 耗時 15145 ms
- 抽到的 JSON:
```json
{
  "Part Number": "DFLS160",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.93,
  "Maximum Width (mm)": 3.9,
  "Maximum Height (mm)": 1.0,
  "PIN Number": 2,
  "I_O、I_F (A)": 1.0,
  "V_F(Forward Voltage) (V)": "0.50 @1.0A",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 60,
  "I_R(Reverse Current) ": "0.1mA @60V,25°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1119 ms
- Prompt: 13966 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 18696 ms
- 最終 JSON:
```json
{
  "Part Number": "DFLS160",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.93,
  "Maximum Width (mm)": 3.9,
  "Maximum Height (mm)": 1.0,
  "PIN Number": 2,
  "I_O、I_F (A)": 1.0,
  "V_F(Forward Voltage) (V)": "0.50 @1.0A",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 60,
  "I_R(Reverse Current) ": "0.1mA @60V,25°C"
}
```