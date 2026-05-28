# BAS16

_Cell: `v20_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T13:58:05.287787_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 8 張（頁碼 [4, 5, 6, 8, 9, 1, 2, 3]）
- 耗時: 3594 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21760 字元 + 8 張圖
- Response: 461 字元, 耗時 21745 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 3.0,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.215,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、0.5µA @80V、30µA @25V,150°C、50µA @80V,150°C"
}
```

### Validator
- ⚠️ 1 條 fix:
  - `I_R: '30nA @25V、0.5µA @80V、30µA @25V,150°C、50µA @80V,150°C' → '30nA @25V、0.5uA @80V、30uA @25V,150°C、50uA @80V,150°C'`

### Critic (conservative)
- ✅ PASS, 耗時 1894 ms
- Prompt: 14033 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 27239 ms
- 最終 JSON:
```json
{
  "Part Number": "BAS16",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 3.0,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.215,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、0.5uA @80V、30uA @25V,150°C、50uA @80V,150°C"
}
```