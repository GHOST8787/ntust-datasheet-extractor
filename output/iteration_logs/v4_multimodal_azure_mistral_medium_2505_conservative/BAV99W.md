# BAV99W

_Cell: `v4_multimodal_azure_mistral_medium_2505_conservative`  ·  Started: 2026-05-22T10:06:05.579946_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [2, 3, 4]）
- 耗時: 686 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 17847 字元 + 3 張圖
- Response: 431 字元, 耗時 12032 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.9,
  "Maximum Width (mm)": 1.0,
  "Maximum Height (mm)": 0.5,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1479 ms
- Prompt: 14004 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 14203 ms
- 最終 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.9,
  "Maximum Width (mm)": 1.0,
  "Maximum Height (mm)": 0.5,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```