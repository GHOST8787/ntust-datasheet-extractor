# BAS16

_Cell: `v29_multimodal_azure_gpt_4o_conservative`  ·  Started: 2026-05-22T16:20:18.272014_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 8 張（頁碼 [1, 2, 3, 4, 5, 6, 8, 9]）
- 耗時: 3175 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 22114 字元 + 8 張圖
- Response: 471 字元, 耗時 20181 ms
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
  "I_R(Reverse Current) ": "30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C"
}
```

### Validator
- ⚠️ 1 條 fix:
  - `I_R: '30nA @25V,25°C、0.5µA @80V,25°C、30µA @25V,150°C、50µA @80V,150°C' → '30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C'`

### Critic (conservative)
- ✅ PASS, 耗時 1546 ms
- Prompt: 14043 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 25008 ms
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
  "I_R(Reverse Current) ": "30nA @25V,25°C、0.5uA @80V,25°C、30uA @25V,150°C、50uA @80V,150°C"
}
```