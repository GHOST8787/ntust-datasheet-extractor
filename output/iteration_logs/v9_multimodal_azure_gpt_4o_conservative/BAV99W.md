# BAV99W

_Cell: `v9_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T11:11:32.688823_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [2, 3, 4, 5, 6]）
- 耗時: 1283 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 19091 字元 + 5 張圖
- Response: 432 字元, 耗時 19412 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.2,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 1.1,
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
- ✅ PASS, 耗時 2766 ms
- Prompt: 14005 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 23464 ms
- 最終 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.2,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```