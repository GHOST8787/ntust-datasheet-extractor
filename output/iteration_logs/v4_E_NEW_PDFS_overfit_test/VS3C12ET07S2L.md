# VS3C12ET07S2L

_Cell: `v4_E_NEW_PDFS_overfit_test`  ·  Started: 2026-05-22T10:42:29.071525_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 3 張（頁碼 [1, 2, 3]）
- 耗時: 1930 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 17875 字元 + 3 張圖
- Response: 457 字元, 耗時 10878 ms
- 抽到的 JSON:
```json
{
  "Part Number": "VS3C12ET07S2L",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": null,
  "Maximum Width (mm)": null,
  "Maximum Height (mm)": null,
  "PIN Number": 2,
  "I_O、I_F (A)": 12,
  "V_F(Forward Voltage) (V)": "1.3 @12A、1.5 @12A,150°C、1.58 @12A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "0.8uA @650V、3uA @650V,150°C、5uA @650V,175°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1437 ms
- Prompt: 14037 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 14248 ms
- 最終 JSON:
```json
{
  "Part Number": "VS3C12ET07S2L",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": null,
  "Maximum Width (mm)": null,
  "Maximum Height (mm)": null,
  "PIN Number": 2,
  "I_O、I_F (A)": 12,
  "V_F(Forward Voltage) (V)": "1.3 @12A、1.5 @12A,150°C、1.58 @12A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "0.8uA @650V、3uA @650V,150°C、5uA @650V,175°C"
}
```