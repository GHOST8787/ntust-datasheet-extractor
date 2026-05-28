# BAV99W

_Cell: `v16_multimodal_azure_gpt_4o_hybrid`  ·  Started: 2026-05-22T12:34:53.532215_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [2, 3, 4, 5, 6]）
- 耗時: 1385 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 432 字元, 耗時 21194 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.2,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 0.9,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 10482 ms
- Prompt: 13472 字元, Response: 450 字元
- 3 條 corrections:
  - Maximum Length (mm): The provided value is 2.2 mm, but the datasheet specifies the maximum length as 2.5 mm. Update to 2.5 mm.
  - Maximum Width (mm): The provided value is 1.35 mm, but the datasheet specifies the maximum width as 1.3 mm. Update to 1.3 mm.
  - Maximum Height (mm): The provided value is 0.9 mm, but the datasheet specifies the maximum height as 0.95 mm. Update to 0.95 mm.

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22758 字元 + 5 張圖
- Response: 432 字元, 耗時 14944 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.5,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 0.95,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 10034 ms
- Prompt: 13472 字元, Response: 320 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 2.4 as per the datasheet (2.4 ± 0.1 mm).
  - Maximum Width (mm) should be corrected to 1.3 as per the datasheet (1.3 ± 0.1 mm).
  - Maximum Height (mm) should be corrected to 0.9 as per the datasheet (0.9 ± 0.1 mm).

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 22627 字元 + 5 張圖
- Response: 431 字元, 耗時 13908 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.4,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 0.9,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (hybrid)
- ❌ FAIL, 耗時 11225 ms
- Prompt: 13471 字元, Response: 325 字元
- 3 條 corrections:
  - Maximum Length (mm) should be corrected to 2.5 as per the datasheet (A Max = 2.5 mm).
  - Maximum Width (mm) should be corrected to 1.3 as per the datasheet (D Max = 1.3 mm).
  - Maximum Height (mm) should be corrected to 0.9 as per the datasheet (E Max = 0.9 mm).

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 83182 ms
- 最終 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.4,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 0.9,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```