# BAV99W

_Cell: `v13_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T11:51:37.784823_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [2, 3, 4, 5, 6]）
- 耗時: 1333 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 22510 字元 + 5 張圖
- Response: 431 字元, 耗時 13420 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.5,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 0.9,
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
- ✅ PASS, 耗時 3211 ms
- Prompt: 14004 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 17969 ms
- 最終 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.5,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 0.9,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```