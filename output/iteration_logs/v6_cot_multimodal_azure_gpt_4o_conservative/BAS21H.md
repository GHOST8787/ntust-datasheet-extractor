# BAS21H

_Cell: `v6_cot_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T09:38:12.092876_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [1, 2, 3]）
- 耗時: 2334 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 18641 字元 + 3 張圖
- Response: 725 字元, 耗時 22490 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.7,
  "Maximum Width (mm)": 1.25,
  "Maximum Height (mm)": 0.85,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1632 ms
- Prompt: 14298 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 26461 ms
- 最終 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.7,
  "Maximum Width (mm)": 1.25,
  "Maximum Height (mm)": 0.85,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```