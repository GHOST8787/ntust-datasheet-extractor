# MSB30M

_Cell: `v16_multimodal_azure_gpt_4o_hybrid`  ·  Started: 2026-05-22T12:41:21.553882_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 3589 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 464 字元, 耗時 21046 ms
- 抽到的 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 6.7,
  "Maximum Width (mm)": 7.4,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 15393 ms
- Prompt: 13504 字元, Response: 386 字元
- 3 條 corrections:
  - Maximum Length (mm): Provided value is 6.7 mm, but datasheet specifies D Max as 6.70 mm. This is correct.
  - Maximum Width (mm): Provided value is 7.4 mm, but datasheet specifies E Max as 7.40 mm. This is correct.
  - Maximum Height (mm): Provided value is 1.5 mm, but datasheet specifies A Max as 1.50 mm. This is correct.

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22725 字元 + 5 張圖
- Response: 464 字元, 耗時 14890 ms
- 抽到的 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 6.7,
  "Maximum Width (mm)": 7.4,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 11476 ms
- Prompt: 13504 字元, Response: 329 字元
- 3 條 corrections:
  - Maximum Length (mm): Should be corrected to 6.7 mm as per datasheet (D Max = 6.70 mm).
  - Maximum Width (mm): Should be corrected to 7.4 mm as per datasheet (E Max = 7.40 mm).
  - Maximum Height (mm): Should be corrected to 1.5 mm as per datasheet (A Max = 1.50 mm).

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 22668 字元 + 5 張圖
- Response: 464 字元, 耗時 16712 ms
- 抽到的 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 6.7,
  "Maximum Width (mm)": 7.4,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 159672 ms
- Prompt: 13504 字元, Response: 302 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 6.70 as per the datasheet (D Max).
  - Maximum Width (mm) should be corrected to 7.40 as per the datasheet (E Max).
  - Maximum Height (mm) should be corrected to 1.50 as per the datasheet (A Max).

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 242787 ms
- 最終 JSON:
```json
{
  "Part Number": "MSB30M",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 6.7,
  "Maximum Width (mm)": 7.4,
  "Maximum Height (mm)": 1.5,
  "PIN Number": 4,
  "I_O、I_F (A)": 3.0,
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1000V,25°C、500uA @1000V,125°C"
}
```