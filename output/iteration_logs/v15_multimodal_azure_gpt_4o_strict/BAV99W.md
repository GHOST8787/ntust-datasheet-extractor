# BAV99W

_Cell: `v15_multimodal_azure_gpt_4o_strict`  ·  Started: 2026-05-22T12:13:03.507471_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [2, 3, 4, 5, 6]）
- 耗時: 1771 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 432 字元, 耗時 10811 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.2,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 9180 ms
- Prompt: 14765 字元, Response: 595 字元
- 5 條 corrections:
  - Maximum Length (mm): 現值 '2.2' 不正確，應改為 '2.5'，因為 datasheet Package Dimensions 表中標示最大值為 2.5 mm。
  - Maximum Width (mm): 現值 '1.35' 不正確，應改為 '1.3'，因為 datasheet Package Dimensions 表中標示最大值為 1.3 mm。
  - Maximum Height (mm): 現值 '1.1' 不正確，應改為 '1.1'，但應確認是否為 Package Dimensions 表中的最大值，datasheet 中未明確標示最大高度。
  - I_O、I_F (A): 現值 '0.15' 不正確，應改為 '0.150'，因為 datasheet 中 Average rectified current (I_O) 為 150 mA，需轉換為 A。
  - I_R(Reverse Current): 現值 '30nA @25V、200nA @80V' 漏抓高溫條件，datasheet Electrical Characteristics 表中列出 25°C 和 150°C 的條件，應補充高溫條件。

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22892 字元 + 5 張圖
- Response: 431 字元, 耗時 10888 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.5,
  "Maximum Width (mm)": 1.3,
  "Maximum Height (mm)": 1.1,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 16169 ms
- Prompt: 14764 字元, Response: 455 字元
- 4 條 corrections:
  - Maximum Length (mm): 現值 '2.5' 應改為 '2.6'，datasheet Package Dimensions 表中標示最大值為 2.6 mm。
  - Maximum Width (mm): 現值 '1.3' 應改為 '1.4'，datasheet Package Dimensions 表中標示最大值為 1.4 mm。
  - Maximum Height (mm): 現值 '1.1' 應改為 '1.2'，datasheet Package Dimensions 表中標示最大值為 1.2 mm。
  - I_R(Reverse Current): 現值 '30nA @25V、200nA @80V' 漏抓高溫條件，datasheet Electrical Characteristics 表中列出 25°C 和 150°C 的條件，應補充高溫條件。

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 22757 字元 + 5 張圖
- Response: 431 字元, 耗時 11308 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.6,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.2,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 11633 ms
- Prompt: 14764 字元, Response: 472 字元
- 4 條 corrections:
  - Maximum Length (mm): 現值 '2.6' 不正確，應改為 '2.5'，因為 datasheet Package Dimensions 表中標示最大值為 2.5 mm。
  - Maximum Width (mm): 現值 '1.4' 不正確，應改為 '1.3'，因為 datasheet Package Dimensions 表中標示最大值為 1.3 mm。
  - Maximum Height (mm): 現值 '1.2' 不正確，應改為 '1.1'，因為 datasheet Package Dimensions 表中標示最大值為 1.1 mm。
  - I_R(Reverse Current): 現值 '30nA @25V、200nA @80V' 漏抓高溫條件，datasheet Electrical Characteristics 表中還列出 150°C 條件，應補充高溫條件的數據。

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 71769 ms
- 最終 JSON:
```json
{
  "Part Number": "BAV99W",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 2.6,
  "Maximum Width (mm)": 1.4,
  "Maximum Height (mm)": 1.2,
  "PIN Number": 3,
  "I_O、I_F (A)": 0.15,
  "V_F(Forward Voltage) (V)": "0.715 @1mA、0.855 @10mA、1.0 @50mA、1.25 @150mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 100,
  "I_R(Reverse Current) ": "30nA @25V、200nA @80V"
}
```