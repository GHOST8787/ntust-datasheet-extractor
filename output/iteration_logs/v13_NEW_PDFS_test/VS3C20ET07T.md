# VS3C20ET07T

_Cell: `v13_NEW_PDFS_test`  ·  Started: 2026-05-22T11:55:23.563842_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 3349 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 22530 字元 + 6 張圖
- Response: 464 字元, 耗時 17547 ms
- 抽到的 JSON:
```json
{
  "Part Number": "VS3C20ET07T",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 10.51,
  "Maximum Width (mm)": 8.89,
  "Maximum Height (mm)": 4.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 20.0,
  "V_F(Forward Voltage) (V)": "1.5 @20A, 1.85 @20A,150°C, 1.6 @20A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "100uA @650V, 250uA @650V,150°C, 9uA @650V,175°C"
}
```

### Validator
- ⚠️ 2 條 fix:
  - `V_F: '1.5 @20A, 1.85 @20A,150°C, 1.6 @20A,175°C' → '1.5 @20A、1.85 @20A,150°C、1.6 @20A,175°C'`
  - `I_R: '100uA @650V, 250uA @650V,150°C, 9uA @650V,175°C' → '100uA @650V、250uA @650V,150°C、9uA @650V,175°C'`

### Critic (conservative)
- ✅ PASS, 耗時 1366 ms
- Prompt: 14038 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 22267 ms
- 最終 JSON:
```json
{
  "Part Number": "VS3C20ET07T",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 10.51,
  "Maximum Width (mm)": 8.89,
  "Maximum Height (mm)": 4.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 20.0,
  "V_F(Forward Voltage) (V)": "1.5 @20A、1.85 @20A,150°C、1.6 @20A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "100uA @650V、250uA @650V,150°C、9uA @650V,175°C"
}
```