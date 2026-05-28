# SBR05U20LPS

_Cell: `v15_multimodal_azure_gpt_4o_strict`  ·  Started: 2026-05-22T12:20:11.924264_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 2914 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21784 字元 + 5 張圖
- Response: 501 字元, 耗時 26506 ms
- 抽到的 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、50uA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 34629 ms
- Prompt: 14849 字元, Response: 1056 字元
- 6 條 corrections:
  - Minimum Operating Temperature(°C): 現值 '-65' 錯誤，應改為 '-55'，因為 datasheet 中的 Tj (Operating Junction Temperature) 範圍是 -65°C 至 +150°C，但 Tj 應取 -55°C 至 +150°C。
  - Maximum Length (mm): 現值 '1.075' 錯誤，應改為 null，因為 datasheet 中的 Package Outline Dimensions 表中 D 的最大值是 1.075 mm，但這是封裝尺寸，應取焊墊尺寸。
  - Maximum Width (mm): 現值 '0.675' 錯誤，應改為 null，因為 datasheet 中的 Package Outline Dimensions 表中 E 的最大值是 0.675 mm，但這是封裝尺寸，應取焊墊尺寸。
  - Maximum Height (mm): 現值 '0.4' 錯誤，應改為 null，因為 datasheet 中的 Package Outline Dimensions 表中 A 的最大值是 0.4 mm，但這是封裝尺寸，應取焊墊尺寸。
  - V_F(Forward Voltage) (V): 現值 '0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C' 錯誤，應改為 '0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C'，因為 datasheet
  - I_R(Reverse Current): 現值 '6uA @20V,25°C、50uA @20V,150°C' 錯誤，應改為 '6uA @20V,25°C、50uA @20V,150°C'，因為 datasheet 中的 Leakage Current 表列出了這些條件，但現值中有些條件未正確對應。

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 23438 字元 + 5 張圖
- Response: 501 字元, 耗時 17470 ms
- 抽到的 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、50uA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 16591 ms
- Prompt: 14849 字元, Response: 709 字元
- 10 條 corrections:
  - Minimum Operating Temperature(°C): 現值 -55，應改為 -65；datasheet 中 Tj 和 Tstg 範圍均為 -65 至 +150°C，應取 Tj。
  - Maximum Operating Temperature(°C): 現值 150，應改為 150；但需明確標註為 Tj。
  - Maximum Length (mm): 現值 1.075，正確；無需修正。
  - Maximum Width (mm): 現值 0.675，正確；無需修正。
  - Maximum Height (mm): 現值 0.4，正確；無需修正。
  - PIN Number: 現值 2，正確；無需修正。
  - I_O、I_F (A): 現值 0.5，正確；無需修正。
  - V_F(Forward Voltage) (V): 現值 '0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C'，正確；無需修正。
  - V_RRM(Peak Repetitive Reverse Voltage) (V): 現值 20，正確；無需修正。
  - I_R(Reverse Current): 現值 '6uA @20V,25°C、50uA @20V,150°C'，正確；無需修正。

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 23071 字元 + 5 張圖
- Response: 501 字元, 耗時 13963 ms
- 抽到的 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、50uA @20V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 12226 ms
- Prompt: 14849 字元, Response: 717 字元
- 6 條 corrections:
  - Minimum Operating Temperature(°C): 現值 '-65' 是 Tstg (Storage Temperature) 的值，應改為 Tj (Junction Temperature) 的最小值 '-55'。
  - Maximum Length (mm): 現值 '1.075' 是正確的，但應確認來自 Package Outline Dimensions 表的 MAX 欄。
  - Maximum Width (mm): 現值 '0.675' 是正確的，但應確認來自 Package Outline Dimensions 表的 MAX 欄。
  - Maximum Height (mm): 現值 '0.4' 是正確的，但應確認來自 Package Outline Dimensions 表的 MAX 欄。
  - V_F(Forward Voltage) (V): 現值 '0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C' 中，條件應簡化為 '@100mA' 等格式，且應確認所有條件是否完整。
  - I_R(Reverse Current): 現值 '6uA @20V,25°C、50uA @20V,150°C' 漏抓了 datasheet 中的另一條件 '1.5mA @20V,150°C'，應補充完整。

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 124321 ms
- 最終 JSON:
```json
{
  "Part Number": "SBR05U20LPS",
  "Minimum Operating Temperature(°C)": -65,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.075,
  "Maximum Width (mm)": 0.675,
  "Maximum Height (mm)": 0.4,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.5,
  "V_F(Forward Voltage) (V)": "0.38 @0.1A,25°C、0.28 @0.1A,150°C、0.42 @0.2A,25°C、0.34 @0.2A,150°C、0.50 @0.5A,25°C、0.45 @0.5A,150°C",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 20,
  "I_R(Reverse Current) ": "6uA @20V,25°C、50uA @20V,150°C"
}
```