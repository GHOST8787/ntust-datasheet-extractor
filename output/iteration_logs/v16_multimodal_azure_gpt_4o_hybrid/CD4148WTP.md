# CD4148WTP

_Cell: `v16_multimodal_azure_gpt_4o_hybrid`  ·  Started: 2026-05-22T12:36:16.715966_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 8820 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 1561 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 18580 字元 + 6 張圖
- Response: 412 字元, 耗時 25923 ms
- 抽到的 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.55,
  "Maximum Width (mm)": 0.8,
  "Maximum Height (mm)": 0.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 9003 ms
- Prompt: 10259 字元, Response: 305 字元
- 3 條 corrections:
  - Maximum Length (mm): Should be corrected to 1.65 (1.55 + 0.1 as per datasheet).
  - Maximum Width (mm): Should be corrected to 0.9 (0.8 + 0.1 as per datasheet).
  - Maximum Height (mm): Should be corrected to 0.75 (0.65 + 0.1 as per datasheet).

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 19409 字元 + 6 張圖
- Response: 412 字元, 耗時 10205 ms
- 抽到的 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.65,
  "Maximum Width (mm)": 0.9,
  "Maximum Height (mm)": 0.75,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 9000 ms
- Prompt: 10259 字元, Response: 306 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 1.55 as per datasheet (L: 1.55±0.1).
  - Maximum Width (mm) should be corrected to 0.8 as per datasheet (W: 0.80±0.1).
  - Maximum Height (mm) should be corrected to 0.65 as per datasheet (T: 0.65±0.1).

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 19410 字元 + 6 張圖
- Response: 412 字元, 耗時 11787 ms
- 抽到的 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.55,
  "Maximum Width (mm)": 0.8,
  "Maximum Height (mm)": 0.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 9636 ms
- Prompt: 10259 字元, Response: 302 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 1.65 (1.55 + 0.1 as per datasheet).
  - Maximum Width (mm) should be corrected to 0.9 (0.8 + 0.1 as per datasheet).
  - Maximum Height (mm) should be corrected to 0.75 (0.65 + 0.1 as per datasheet).

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 77124 ms
- 最終 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.55,
  "Maximum Width (mm)": 0.8,
  "Maximum Height (mm)": 0.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```