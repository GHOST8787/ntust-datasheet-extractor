# MSB30M

_Cell: `v15_multimodal_azure_gpt_4o_strict`  ·  Started: 2026-05-22T12:18:26.362706_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 3383 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 464 字元, 耗時 22843 ms
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

### Critic (strict)
- ❌ FAIL, 耗時 14831 ms
- Prompt: 14797 字元, Response: 613 字元
- 4 條 corrections:
  - Maximum Width (mm): 現值 '7.4'，應改為 '7.40'，datasheet 中 Package Outline Dimensions 表的最大值為 7.40。
  - Maximum Height (mm): 現值 '1.5'，應改為 '1.50'，datasheet 中 Package Outline Dimensions 表的最大值為 1.50。
  - V_F(Forward Voltage) (V): 現值 '1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.8 @1.5A,25°C'，應改為 '1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.80 @1.5A,25°C'，datasheet 中 Forward Voltage 表明 0.80V 而非 0.8V。
  - I_R(Reverse Current): 現值 '5uA @1000V,25°C、500uA @1000V,125°C'，應改為 '5uA @1,000V,25°C、500uA @1,000V,125°C'，datasheet 中條件的電壓標示為 '1,000V'，應保持一致。

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22948 字元 + 5 張圖
- Response: 470 字元, 耗時 12613 ms
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
  "V_F(Forward Voltage) (V)": "1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.80 @1.5A,25°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1,000V,25°C、500uA @1,000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 13763 ms
- Prompt: 14800 字元, Response: 706 字元
- 4 條 corrections:
  - Maximum Width (mm): 現值 '7.4'，應改為 '7.40'，datasheet 中 Package Outline Dimensions 表格中 E 的最大值為 7.40。
  - Maximum Height (mm): 現值 '1.5'，應改為 '1.50'，datasheet 中 Package Outline Dimensions 表格中 A 的最大值為 1.50。
  - V_F(Forward Voltage) (V): 現值 '1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.80 @1.5A,25°C'，應改為 '1.1 @3.0A,25°C、1.02 @3.0A,125°C、0.88 @1.5A,125°C、0.80 @1.5A,25°C'，但需調整順序為 '0.80 @1.5A,25°C、0.88 @1.5A,125°C、1.1 @3.0A,25°C、1.02 @3.0A,125°C'，以符合 data
  - I_R(Reverse Current): 現值 '5uA @1,000V,25°C、500uA @1,000V,125°C'，應改為 '5uA @1,000V,25°C、500uA @1,000V,125°C'，但需調整順序為 '5uA @1,000V,25°C、500uA @1,000V,125°C'，以符合 datasheet 中的順序。

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 23044 字元 + 5 張圖
- Response: 470 字元, 耗時 12681 ms
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
  "V_F(Forward Voltage) (V)": "0.80 @1.5A,25°C、0.88 @1.5A,125°C、1.1 @3.0A,25°C、1.02 @3.0A,125°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1,000V,25°C、500uA @1,000V,125°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 25433 ms
- Prompt: 14800 字元, Response: 688 字元
- 5 條 corrections:
  - Maximum Width (mm): 現值 '7.4'，應改為 '7.40'，因為 datasheet 明確標示最大值為 7.40。
  - Maximum Height (mm): 現值 '1.5'，應改為 '1.50'，因為 datasheet 明確標示最大值為 1.50。
  - V_F(Forward Voltage) (V): 現值 '0.80 @1.5A,25°C、0.88 @1.5A,125°C、1.1 @3.0A,25°C、1.02 @3.0A,125°C'，應改為 '0.80 @1.5A,25°C、0.88 @1.5A,125°C、1.02 @3.0A,25°C、1.10 @3.0A,125°C'，因為 datasheet 中 3.0A, 125°C 條件的最大值為 1.10。
  - V_RRM(Peak Repetitive Reverse Voltage) (V): 現值 '1000'，應改為 '1,000'，因為 datasheet 使用千位分隔符號。
  - I_R(Reverse Current): 現值 '5uA @1,000V,25°C、500uA @1,000V,125°C'，應改為 '5uA @1,000V,25°C、500uA @1,000V,125°C、0.31uA @1,000V,25°C'，因為 datasheet 中還列出了 25°C 條件下的典型值 0.31uA，應補充。

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 105560 ms
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
  "V_F(Forward Voltage) (V)": "0.80 @1.5A,25°C、0.88 @1.5A,125°C、1.1 @3.0A,25°C、1.02 @3.0A,125°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 1000,
  "I_R(Reverse Current) ": "5uA @1,000V,25°C、500uA @1,000V,125°C"
}
```