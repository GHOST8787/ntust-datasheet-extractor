# BAV99W

_Cell: `v18_multimodal_azure_llama_4_maverick_conservative`  ·  Started: 2026-05-22T13:02:40.428564_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [2, 3, 4, 5, 6]）
- 耗時: 885 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 409 字元, 耗時 4524 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.1,
  "Maximum Width (mm)": 1.25,
  "Maximum Height (mm)": 0.9,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.00 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 725 ms
- Prompt: 14006 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 6138 ms
- 最終 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.1,
  "Maximum Width (mm)": 1.25,
  "Maximum Height (mm)": 0.9,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.00 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```