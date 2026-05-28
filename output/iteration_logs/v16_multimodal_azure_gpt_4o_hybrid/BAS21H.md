# BAS21H

_Cell: `v16_multimodal_azure_gpt_4o_hybrid`  ·  Started: 2026-05-22T12:30:20.277238_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 2107 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 418 字元, 耗時 17310 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.8,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 1.0,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 22786 ms
- Prompt: 13458 字元, Response: 365 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 1.7 (from 1.8) based on the datasheet's 'D Max' value.
  - Maximum Width (mm) should be corrected to 1.25 (from 1.35) based on the datasheet's 'E Max' value.
  - Maximum Height (mm) should be corrected to 0.85 (from 1.0) based on the datasheet's 'A Max' value.

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22658 字元 + 5 張圖
- Response: 419 字元, 耗時 32075 ms
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

### Critic (hybrid)
- ✅ PASS, 耗時 25886 ms
- Prompt: 13459 字元, Response: 45 字元

## Final
- 跑完輪數: 2
- Critic 最終: ✅ PASS
- 總耗時: 100170 ms
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