# BAS21H

_Cell: `v15_multimodal_azure_gpt_4o_strict`  ·  Started: 2026-05-22T12:10:09.707045_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 12016 字元
- 圖片: 5 張（頁碼 [1, 2, 3, 4, 5]）
- 耗時: 2297 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 21764 字元 + 5 張圖
- Response: 418 字元, 耗時 7161 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.8,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 1.0,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 12052 ms
- Prompt: 14751 字元, Response: 627 字元
- 5 條 corrections:
  - Maximum Length (mm): 現值 '1.8' 應改為 '1.7'，datasheet 的 Mechanical Case Outline 表中 MAX 值為 1.7 mm。
  - Maximum Width (mm): 現值 '1.35' 應改為 '1.25'，datasheet 的 Mechanical Case Outline 表中 MAX 值為 1.25 mm。
  - Maximum Height (mm): 現值 '1.0' 應改為 '0.85'，datasheet 的 Mechanical Case Outline 表中 MAX 值為 0.85 mm。
  - V_F(Forward Voltage) (V): 現值 '1.0 @100mA、1.25 @200mA' 漏抓 1000mV (1.0V) @100mA 和 1250mV (1.25V) @200mA 的單位換算，應改為 '1.0 @100mA、1.25 @200mA'。
  - I_R(Reverse Current): 現值 '0.1uA @200V、100uA @200V,150°C' 漏抓條件 '25°C'，應改為 '0.1uA @200V,25°C、100uA @200V,150°C'，以完整列出所有條件。

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 22911 字元 + 5 張圖
- Response: 424 字元, 耗時 10102 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.7,
  "Maximum Width (mm)": 1.25,
  "Maximum Height (mm)": 0.85,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V,25°C、100uA @200V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 11344 ms
- Prompt: 14757 字元, Response: 1074 字元
- 5 條 corrections:
  - Maximum Length (mm): Current value '1.7' is incorrect. The datasheet specifies the maximum length as '1.8 mm' in the Mechanical Case Outline table.
  - Maximum Width (mm): Current value '1.25' is incorrect. The datasheet specifies the maximum width as '1.35 mm' in the Mechanical Case Outline table.
  - Maximum Height (mm): Current value '0.85' is incorrect. The datasheet specifies the maximum height as '0.95 mm' in the Mechanical Case Outline table.
  - V_F(Forward Voltage) (V): Current value '1.0 @100mA、1.25 @200mA' is incomplete. The datasheet specifies forward voltage values for 100 mA (1.0 V) and 200 mA (1.25 V), but the units are in mV and need to be converted to V. Correct value: '1.0 @100mA、1
  - I_R(Reverse Current): Current value '0.1uA @200V,25°C、100uA @200V,150°C' is incomplete. The datasheet specifies reverse current conditions for 200 V at 25°C (0.1 µA) and 150°C (100 µA), but the units should use 'uA' consistently. Correct value: '0.1u

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 23364 字元 + 5 張圖
- Response: 419 字元, 耗時 11560 ms
- 抽到的 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.8,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 0.95,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 14635 ms
- Prompt: 14752 字元, Response: 669 字元
- 5 條 corrections:
  - Maximum Length (mm): 現值 '1.8' 應改為 '1.7'，datasheet 的 Mechanical Case Outline 表中 MAX 值為 1.7 mm。
  - Maximum Width (mm): 現值 '1.35' 應改為 '1.25'，datasheet 的 Mechanical Case Outline 表中 MAX 值為 1.25 mm。
  - Maximum Height (mm): 現值 '0.95' 應改為 '0.85'，datasheet 的 Mechanical Case Outline 表中 MAX 值為 0.85 mm。
  - V_F(Forward Voltage) (V): 現值 '1.0 @100mA、1.25 @200mA' 漏抓 10mA 條件；datasheet Electrical Characteristics 表列了 10mA、100mA 和 200mA 三個條件，應補充 '0.715 @10mA'。
  - I_R(Reverse Current): 現值 '0.1uA @200V、100uA @200V,150°C' 漏抓 25°C 條件；datasheet Electrical Characteristics 表列了 25°C 和 150°C 兩個條件，應補充 '0.1uA @200V,25°C'。

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 69160 ms
- 最終 JSON:
```json
{
  "Part Number": "BAS21H",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.8,
  "Maximum Width (mm)": 1.35,
  "Maximum Height (mm)": 0.95,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.2,
  "V_F(Forward Voltage) (V)": "1.0 @100mA、1.25 @200mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 250,
  "I_R(Reverse Current) ": "0.1uA @200V、100uA @200V,150°C"
}
```