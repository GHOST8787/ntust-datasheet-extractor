# FFSH5065B

_Cell: `v29_NEW_PDFS_test`  ·  Started: 2026-05-22T16:23:32.033670_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 3073 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 22130 字元 + 6 張圖
- Response: 468 字元, 耗時 20031 ms
- 抽到的 JSON:
```json
{
  "Part Number": "FFSH5065B",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 20.82,
  "Maximum Width (mm)": 15.87,
  "Maximum Height (mm)": 4.82,
  "PIN Number": 2,
  "I_O、I_F (A)": 50.0,
  "V_F(Forward Voltage) (V)": "1.7 @50A,25°C、2.0 @50A,125°C、2.4 @50A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "40uA @650V,25°C、80uA @650V,125°C、160uA @650V,175°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 8666 ms
- Prompt: 14044 字元, Response: 44 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 31778 ms
- 最終 JSON:
```json
{
  "Part Number": "FFSH5065B",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 20.82,
  "Maximum Width (mm)": 15.87,
  "Maximum Height (mm)": 4.82,
  "PIN Number": 2,
  "I_O、I_F (A)": 50.0,
  "V_F(Forward Voltage) (V)": "1.7 @50A,25°C、2.0 @50A,125°C、2.4 @50A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "40uA @650V,25°C、80uA @650V,125°C、160uA @650V,175°C"
}
```