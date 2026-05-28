# BAS21H

_Cell: `v4_multimodal_azure_mistral_medium_2505_conservative`  ·  Started: 2026-05-22T10:05:02.331756_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [1, 2, 3]）
- 耗時: 1694 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 17847 字元 + 3 張圖
- Response: 417 字元, 耗時 13604 ms
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
  "V_F(Forward Voltage) (V)": "1 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ❌ FAIL, 耗時 6565 ms
- Prompt: 13990 字元, Response: 418 字元
- 2 條 corrections:
  - V_F(Forward Voltage) (V) 應為 "1.0 @100mA、1.25 @200mA"，因為 datasheet Page 2 明確標示 Forward Voltage (IF=100mAdc) Max=1000mV (1.0V) 和 (IF=200mAdc) Max=1250mV (1.25V)，原答案單位換算正確但格式需統一
  - I_R(Reverse Current) 應為 "0.1uA @200V、100uA @200V,150°C"，因為 datasheet Page 2 明確標示 Reverse Voltage Leakage Current (VR=200Vdc) Max=0.1uA 和 (VR=200Vdc, TJ=150°C) Max=100uA，原答案格式需調整

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 18795 字元 + 3 張圖
- Response: 419 字元, 耗時 15579 ms
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
- ✅ PASS, 耗時 1722 ms
- Prompt: 13992 字元, Response: 44 字元

## Final
- 跑完輪數: 2
- Critic 最終: ✅ PASS
- 總耗時: 39172 ms
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