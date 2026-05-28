# FFSD1065B

_Cell: `v13_NEW_PDFS_test`  ·  Started: 2026-05-22T11:54:58.445155_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 4423 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 22522 字元 + 6 張圖
- Response: 463 字元, 耗時 19391 ms
- 抽到的 JSON:
```json
{
  "Part Number": "FFSD1065B",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 6.1,
  "Maximum Width (mm)": 6.54,
  "Maximum Height (mm)": 2.29,
  "PIN Number": 3,
  "I_O、I_F (A)": 10,
  "V_F(Forward Voltage) (V)": "1.7 @10A,25°C、2.0 @10A,125°C、2.4 @10A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "40uA @650V,25°C、80uA @650V,125°C、160uA @650V,175°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (conservative)
- ✅ PASS, 耗時 1299 ms
- Prompt: 14039 字元, Response: 45 字元

## Final
- 跑完輪數: 1
- Critic 最終: ✅ PASS
- 總耗時: 25117 ms
- 最終 JSON:
```json
{
  "Part Number": "FFSD1065B",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 175,
  "Maximum Length (mm)": 6.1,
  "Maximum Width (mm)": 6.54,
  "Maximum Height (mm)": 2.29,
  "PIN Number": 3,
  "I_O、I_F (A)": 10,
  "V_F(Forward Voltage) (V)": "1.7 @10A,25°C、2.0 @10A,125°C、2.4 @10A,175°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 650,
  "I_R(Reverse Current) ": "40uA @650V,25°C、80uA @650V,125°C、160uA @650V,175°C"
}
```