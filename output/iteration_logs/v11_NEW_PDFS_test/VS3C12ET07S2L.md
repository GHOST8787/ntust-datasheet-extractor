# VS3C12ET07S2L

_Cell: `v11_NEW_PDFS_test`  ·  Started: 2026-05-22T11:41:18.612393_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 3399 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 20898 字元 + 6 張圖
- Response: 460 字元, 耗時 10523 ms
- 抽到的 JSON:
```json
{
  "Part Number": "VS3C12ET07S2L",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 9.65,
  "Maximum Width (mm)": 10.67,
  "Maximum Height (mm)": 4.06,
  "PIN Number": 2,
  "I_O、I_F (A)": 12,
  "V_F(Forward Voltage) (V)": "1.5 @12A、1.85 @12A,150°C、1.58 @12A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "65uA @650V、150uA @650V,150°C、5uA @650V,175°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1146 ms
- Prompt: 14040 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 15072 ms
- 最終 JSON:
```json
{
  "Part Number": "VS3C12ET07S2L",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 9.65,
  "Maximum Width (mm)": 10.67,
  "Maximum Height (mm)": 4.06,
  "PIN Number": 2,
  "I_O、I_F (A)": 12,
  "V_F(Forward Voltage) (V)": "1.5 @12A、1.85 @12A,150°C、1.58 @12A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "65uA @650V、150uA @650V,150°C、5uA @650V,175°C"
}
```