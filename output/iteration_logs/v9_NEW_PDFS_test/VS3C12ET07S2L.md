# VS3C12ET07S2L

_Cell: `v9_NEW_PDFS_test`  ·  Started: 2026-05-22T11:15:07.621804_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 3894 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 19119 字元 + 6 張圖
- Response: 430 字元, 耗時 14229 ms
- 抽到的 JSON:
```json
{
  "Part Number": "VS3C12ET07S2L",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 10.67,
  "Maximum Width (mm)": 8.0,
  "Maximum Height (mm)": 4.78,
  "PIN Number": 2,
  "I_O、I_F (A)": 12.0,
  "V_F(Forward Voltage) (V)": "1.5 @12A、1.85 @12A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "65uA @650V、150uA @650V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1145 ms
- Prompt: 14009 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 19273 ms
- 最終 JSON:
```json
{
  "Part Number": "VS3C12ET07S2L",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 10.67,
  "Maximum Width (mm)": 8.0,
  "Maximum Height (mm)": 4.78,
  "PIN Number": 2,
  "I_O、I_F (A)": 12.0,
  "V_F(Forward Voltage) (V)": "1.5 @12A、1.85 @12A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "65uA @650V、150uA @650V,150°C"
}
```