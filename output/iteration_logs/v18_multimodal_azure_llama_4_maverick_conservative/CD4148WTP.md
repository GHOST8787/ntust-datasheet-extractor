# CD4148WTP

_Cell: `v18_multimodal_azure_llama_4_maverick_conservative`  ·  Started: 2026-05-22T13:02:46.567671_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 8820 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 1128 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 18580 字元 + 6 張圖
- Response: 412 字元, 耗時 5456 ms
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

### Critic (conservative)
- ✅ PASS, 耗時 670 ms
- Prompt: 10792 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 7258 ms
- 最終 JSON:
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