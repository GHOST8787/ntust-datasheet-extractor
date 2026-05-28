# Baseline Table — Train + Holdout 對照

- **Train set**: 10 parts × 11 fields = 110 cells（specbook.xlsx）
- **Holdout set**: 5 NEW PDFs × 11 fields = 55 cells（evaluate_new_5.py GROUND_TRUTH，手動標）
- **Strict 容差**: numeric ±5% / text token-set ≥ 50%
- **Overfit 判定**: gap > 15% **或** holdout_acc < V4 E baseline (80%)

| Version | Train | Holdout | Gap | Flag |
|---|---|---|---|---|
| V2 GPT-4o baseline | 86/110 = **78.2%** | — | — | — |
| V2 Mistral baseline | 86/110 = **78.2%** | — | — | — |
| V3 D GPT-4o dual×Con | 85/110 = **77.3%** | — | — | — |
| V4 E GPT-4o MM×Con | 89/110 = **80.9%** | — | — | — |
| V5 G strict schema | 85/110 = **77.3%** | — | — | — |
| V6 H CoT | 85/110 = **77.3%** | — | — | — |
| V8 | 93/110 = **84.5%** | 44/55 = **80.0%** | +4.5% | OK |
| V9 | 94/110 = **85.5%** | 49/55 = **89.1%** | -3.6% | OK |
| V10 | 95/110 = **86.4%** | 52/55 = **94.5%** | -8.2% | OK |
| V11 | 95/110 = **86.4%** | 52/55 = **94.5%** | -8.2% | OK |
| V12 | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V13 | 92/110 = **83.6%** | 53/55 = **96.4%** | -12.7% | OK |
| V14 MM critic | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V15 strict critic | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V16 hybrid critic | 92/110 = **83.6%** | 55/55 = **100.0%** | -16.4% | OK |
| V17 temp=0.5 | 95/110 = **86.4%** | 54/55 = **98.2%** | -11.8% | OK |
| V18 Llama-4-Maverick | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V19 ensemble | 94/110 = **85.5%** | — | — | — |
| V20 zoom=4.5 + precision | 94/110 = **85.5%** | 55/55 = **100.0%** | -14.5% | OK |
| V21 crop dimension redo | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V22 toc extractor | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V23 3-model majority | 96/110 = **87.3%** | 55/55 = **100.0%** | -12.7% | OK |
| V24 8-model majority | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V25 cluster-aware vote | 95/110 = **86.4%** | 55/55 = **100.0%** | -13.6% | OK |
| V26 triaxis V18 override | 99/110 = **90.0%** | 55/55 = **100.0%** | -10.0% | OK |
| V27 narrow 4-way | 99/110 = **90.0%** | 55/55 = **100.0%** | -10.0% | OK |
| V28 narrow divergence | 98/110 = **89.1%** | 55/55 = **100.0%** | -10.9% | OK |
| V29 V12+Tj+IO prompt | 96/110 = **87.3%** | 53/55 = **96.4%** | -9.1% | OK |
| V30 V29+V26 logic | 98/110 = **89.1%** | 54/55 = **98.2%** | -9.1% | OK |
| V31 V26+V29 2-field ovr | 100/110 = **90.9%** | 55/55 = **100.0%** | -9.1% | OK |
| V32 V31+Tj regex | 100/110 = **90.9%** | 55/55 = **100.0%** | -9.1% | OK |
| V33 V31+Tj LLM query | 97/110 = **88.2%** | 55/55 = **100.0%** | -11.8% | OK |
| V34 V31+verify-all | 100/110 = **90.9%** | 55/55 = **100.0%** | -9.1% | OK |
| V35 4-way w/ V29 | 99/110 = **90.0%** | 55/55 = **100.0%** | -10.0% | OK |
| V36 V31+Llama critic | 99/110 = **90.0%** | 55/55 = **100.0%** | -10.0% | OK |
| V37 L=max(D,E) swap | 103/110 = **93.6%** | 49/55 = **89.1%** | +4.5% | OK |
| V38 W=H_E override | 100/110 = **90.9%** | 49/55 = **89.1%** | +1.8% | OK |
| V39 L_outer override | 104/110 = **94.5%** | 49/55 = **89.1%** | +5.5% | OK |
| V40 LW outer combined | 106/110 = **96.4%** | 49/55 = **89.1%** | +7.3% | OK |
| V41 Tj single + no Tamb | 106/110 = **96.4%** | 49/55 = **89.1%** | +7.3% | OK |
| V42 Tj regex Tamb | 103/110 = **93.6%** | 49/55 = **89.1%** | +4.5% | OK |
| V43 H_E filtered | 106/110 = **96.4%** | 49/55 = **89.1%** | +7.3% | OK |
| V44 Tj+grep Tamb | 105/110 = **95.5%** | 49/55 = **89.1%** | +6.4% | OK |
| V45 WH anomaly redo | 105/110 = **95.5%** | 49/55 = **89.1%** | +6.4% | OK |
| V46 Llama WH redo | 104/110 = **94.5%** | 51/55 = **92.7%** | +1.8% | OK |
| V47 Llama swap only | 105/110 = **95.5%** | 51/55 = **92.7%** | +2.7% | OK |
| V48 H_E multi-sample | 103/110 = **93.6%** | 51/55 = **92.7%** | +0.9% | OK |

## 每欄位錯誤分佈（取 best train 版本）

Best train version: **V40 LW outer combined** = 96.4%

| Field | Train 錯誤數 | Holdout 錯誤數 |
|---|---|---|
| `Part Number` | 0 | 0 |
| `Minimum Operating Temperature(°C)` | 0 | 0 |
| `Maximum Operating Temperature (°C)` | 0 | 0 |
| `Maximum Length (mm)` | 0 | 3 |
| `Maximum Width (mm)` | 2 | 3 |
| `Maximum Height (mm)` | 2 | 0 |
| `PIN Number` | 0 | 0 |
| `I_O、I_F (A)` | 0 | 0 |
| `V_F(Forward Voltage) (V)` | 0 | 0 |
| `V_RRM(Peak Repetitive Reverse Voltage) (V)` | 0 | 0 |
| `I_R(Reverse Current) ` | 0 | 0 |