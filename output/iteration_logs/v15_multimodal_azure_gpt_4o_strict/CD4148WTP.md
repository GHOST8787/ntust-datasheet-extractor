# CD4148WTP

_Cell: `v15_multimodal_azure_gpt_4o_strict`  ·  Started: 2026-05-22T12:14:15.279814_

## PDF 抽取
- Extractor: `multimodal`
- 文字: 8820 字元
- 圖片: 6 張（頁碼 [1, 2, 3, 4, 5, 6]）
- 耗時: 1876 ms

## Round 1
### Extraction 🖼️ multimodal
- Prompt: 18580 字元 + 6 張圖
- Response: 412 字元, 耗時 12213 ms
- 抽到的 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.55,
  "Maximum Width (mm)": 0.8,
  "Maximum Height (mm)": 0.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 15503 ms
- Prompt: 11558 字元, Response: 771 字元
- 8 條 corrections:
  - Minimum Operating Temperature(°C): 現值 -55 是 Tstg (Storage Temperature) 的範圍，應改為 Tj (Junction Temperature) 的範圍 -55。
  - Maximum Operating Temperature(°C): 現值 150 是 Tstg (Storage Temperature) 的範圍，應改為 Tj (Junction Temperature) 的範圍 150。
  - Maximum Length (mm): 現值 1.55 是正確的，但應標記為 MAX 值，因為表中有 ±0.1 的公差。
  - Maximum Width (mm): 現值 0.8 是正確的，但應標記為 MAX 值，因為表中有 ±0.1 的公差。
  - Maximum Height (mm): 現值 0.65 是正確的，但應標記為 MAX 值，因為表中有 ±0.1 的公差。
  - I_O、I_F (A): 現值 0.1 是錯誤的，應改為 0.1A（100mA ÷ 1000）。
  - V_F(Forward Voltage) (V): 現值 '1.0 @10mA、1.25 @100mA' 漏抓了 '1.0 MAX @10mA' 和 '1.25 MAX @100mA' 的 MAX 標記，應補充。
  - I_R(Reverse Current): 現值 '0.025uA @20V、5uA @75V' 漏抓了 MAX 標記，應補充為 '0.025 MAX uA @20V、5 MAX uA @75V'。

## Round 2
### Extraction 🖼️ multimodal
- Prompt: 19850 字元 + 6 張圖
- Response: 412 字元, 耗時 10288 ms
- 抽到的 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.55,
  "Maximum Width (mm)": 0.8,
  "Maximum Height (mm)": 0.65,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 18358 ms
- Prompt: 11558 字元, Response: 889 字元
- 8 條 corrections:
  - Minimum Operating Temperature(°C): 現值 '-55' 是 Tstg 的值，應改為 Tj 的範圍，datasheet 中 Tj 為 -55°C。
  - Maximum Operating Temperature(°C): 現值 '150' 是 Tstg 的值，應改為 Tj 的範圍，datasheet 中 Tj 為 150°C。
  - Maximum Length (mm): 現值 '1.55' 是正確的，但應標記為 MAX 值，datasheet 中標註為 '1.55±0.1'，應確認 MAX 為 1.65。
  - Maximum Width (mm): 現值 '0.8' 是正確的，但應標記為 MAX 值，datasheet 中標註為 '0.80±0.1'，應確認 MAX 為 0.9。
  - Maximum Height (mm): 現值 '0.65' 是正確的，但應標記為 MAX 值，datasheet 中標註為 '0.65±0.1'，應確認 MAX 為 0.75。
  - I_O、I_F (A): 現值 '0.1' 是錯誤的，應改為 '0.1' (100mA ÷ 1000)，datasheet 中標註為 'IF(AV) = 100mA'。
  - V_F(Forward Voltage) (V): 現值 '1.0 @10mA、1.25 @100mA' 漏抓條件，datasheet 中 Forward Voltage 表列了 '1.0 MAX @10mA' 和 '1.25 MAX @100mA'，應補充 MAX 標註。
  - I_R(Reverse Current): 現值 '0.025uA @20V、5uA @75V' 漏抓條件，datasheet 中列出 '0.025 MAX uA @20V' 和 '5 MAX uA @75V'，應補充 MAX 標註。

## Round 3
### Extraction 🖼️ multimodal
- Prompt: 19968 字元 + 6 張圖
- Response: 412 字元, 耗時 15096 ms
- 抽到的 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.65,
  "Maximum Width (mm)": 0.9,
  "Maximum Height (mm)": 0.75,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```

### Validator
- ✅ 沒有 fix

### Critic (strict)
- ❌ FAIL, 耗時 16963 ms
- Prompt: 11558 字元, Response: 813 字元
- 7 條 corrections:
  - Minimum Operating Temperature(°C): 現值 -55 是 Tstg（Storage Temperature），應改為 Tj（Junction Temperature），datasheet 中 Tj 為 -55°C。
  - Maximum Operating Temperature(°C): 現值 150 是 Tstg（Storage Temperature），應改為 Tj（Junction Temperature），datasheet 中 Tj 為 150°C。
  - Maximum Length (mm): 現值 1.65 是錯誤的，應改為 1.55+0.1=1.65（datasheet 中 Dimension/mm 表的 L MAX）。
  - Maximum Width (mm): 現值 0.9 是錯誤的，應改為 0.80+0.1=0.9（datasheet 中 Dimension/mm 表的 W MAX）。
  - Maximum Height (mm): 現值 0.75 是錯誤的，應改為 0.65+0.1=0.75（datasheet 中 Dimension/mm 表的 T MAX）。
  - V_F(Forward Voltage) (V): 現值 '1.0 @10mA、1.25 @100mA' 漏抓了測試條件的 MAX 標註，應改為 '1.0 MAX @10mA、1.25 MAX @100mA'。
  - I_R(Reverse Current): 現值 '0.025uA @20V、5uA @75V' 漏抓了測試條件的 MAX 標註，應改為 '0.025 MAX uA @20V、5 MAX uA @75V'。

## Final
- 跑完輪數: 3
- Critic 最終: ❌ 撐到 max rounds 強制收尾
- 總耗時: 90310 ms
- 最終 JSON:
```json
{
  "Part Number": "CD4148WTP",
  "Minimum Operating Temperature(°C)": -55,
  "Maximum Operating Temperature (°C)": 150,
  "Maximum Length (mm)": 1.65,
  "Maximum Width (mm)": 0.9,
  "Maximum Height (mm)": 0.75,
  "PIN Number": 2,
  "I_O、I_F (A)": 0.1,
  "V_F(Forward Voltage) (V)": "1.0 @10mA、1.25 @100mA",
  "V_RRM(Peak Repetitive Reverse Voltage) (V)": 75,
  "I_R(Reverse Current) ": "0.025uA @20V、5uA @75V"
}
```