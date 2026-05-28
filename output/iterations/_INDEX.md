# 紀錄文件總索引

> Date: 2026-05-22
> 給 Sunny 寫文章 reference 用

## 🌟 寫文章必讀（從這 3 個開始）

| 檔案 | 用途 |
|---|---|
| `_NARRATIVE.md` | **整體歷程綜述**：3 階段故事線、6 個關鍵 insight、寫文章建議框架 |
| `_FINAL_REPORT.md` | 最終結果摘要：V47 = 95.5%/92.7%、NOT OVERFIT 完整證明、5 個救不動原因 |
| `../baseline_table.md` | 全 V2-V48 版本對照表（train / holdout / gap / overfit flag） |

## 📋 各 iteration 詳細紀錄

### Baseline & 早期 iteration (V12-V19)
| 檔案 | 內容 |
|---|---|
| `baseline_v12_to_v19.md` | V2-V19 全版本對照 + V12 17 errors 細分 + 卡關原因分析 |

### Phase 2 失敗 iteration (V20-V22)
| 檔案 | 內容 |
|---|---|
| `v20_iteration.md` | 高 zoom + page order — train 退步 |
| `v21_iteration.md` | crop dimension redo — 同分 84.5% |
| `v22_iteration.md` | TOC extractor — 同分 84.5% 但救/壞不同 cell |

### Phase 2 首次突破 (V23-V26)
| 檔案 | 內容 |
|---|---|
| `v23_iteration.md` | 3-model majority +1 cell 突破 84.5% 天花板 |
| `v24_v25_iteration.md` | 8-model 跟 cluster vote 失敗實驗 |
| `v26_iteration.md` | triaxis V18 override +3 cell（CD4148WTP）達 88.2% |

### Phase 2 持平期 (V27-V36)
| 檔案 | 內容 |
|---|---|
| `v27_v28_iteration.md` | narrow re-extract 失敗（4-way vote outvote / divergence override 退步）|
| `v29_to_v36.md` | V29 prompt 改 → V36 Llama critic 全部嘗試摘要（V31 +1 達 89.1%）|

### Phase 3 schema rule 突破期 (V37-V48)
| 檔案 | 內容 |
|---|---|
| `v37_to_v48.md` | **V37-V48 全紀錄**：V37 swap → V44 達 95% → V47 final → V48 失敗。每個版本含 cell-level 變化 + NOT OVERFIT 證明 |

### 範本
| 檔案 | 內容 |
|---|---|
| `_template.md` | iteration 文件範本（給未來新 iteration 用）|

## 🗂️ 重要資料檔案

| 路徑 | 內容 |
|---|---|
| `../baseline_table.md` | Markdown 對照表 |
| `../baseline_table.json` | JSON 數據（給後續分析）|
| `../_archive/v47_llama_swap_only/results.json` | **🏆 V47 最佳結果**（train answers）|
| `../iteration_logs/v47_llama_swap_only_NEW_PDFS_test/*.jsonl` | V47 holdout final answers |
| `../_archive/v44_tj_single_grep_tamb/results.json` | V44 train baseline（V47 ancestor）|
| `../iteration_logs/v*_NEW_PDFS_test/` | 各版本 holdout final answers |

## 🐍 Python 腳本（給 reproduce 用）

### 核心 pipeline
| 檔案 | 用途 |
|---|---|
| `../../main.py` | V12 baseline extraction main entry |
| `../../prompts.py` | V12 prompt（28 行 main + V4/V6 變體）|
| `../../prompts_v29.py` | V29 prompt 變體（Tj fallback + I_O 優先）|
| `../../pdf_extractor.py` | multimodal + TOC extractor |
| `../../crop_extractor.py` | dimension anchor crop（V21+）|
| `../../llm_backend.py` | GPT-4o + Llama-4-Maverick + Mistral backend |
| `../../validators.py` | 本地防呆 validator |
| `../../qa_critic.py` | QA critic agent |
| `../../iteration_logger.py` | 雙格式 telemetry logger |

### Run scripts (每個 iteration 一個)
| 範圍 | 檔案 |
|---|---|
| 早期 | `run_v4.py` ~ `run_v18.py` + `run_v19_ensemble.py` |
| Phase 2 | `run_v20.py` ~ `run_v36.py` |
| Phase 3 | `run_v37.py` ~ `run_v48.py` |

### Evaluation
| 檔案 | 用途 |
|---|---|
| `../../evaluate_all.py` | **統一 evaluation**：掃 archive 算 train + holdout，輸出 baseline_table.md |
| `../../evaluate_new_5.py` | NEW PDFs 5 顆 ground truth + evaluation |
| `../../reevaluate.py` | 寬鬆容差重評估 |

## 📊 寫文章資料速查

### 最終結果
```
V47 train:   105/110 = 95.5%
V47 holdout:  51/55  = 92.7%
V47 gap:     +2.7% (train - holdout)
OVERFIT:     NO (gap < 15% AND holdout > 80%)
```

### 6 個 generic 規則（按貢獻排序）
```
V37 L=max(D,E) swap        : +2.7% (3 cells)
V40 LW outer LLM query     : +2.7% (3 cells)
V26 triaxis V18 override   : +2.7% (3 cells)
V44 Tj single + Tamb grep  : +0.9% (1 cell, 達 95%)
V23 3-model majority       : +0.9% (1 cell)
V31 I_O 優先 (2-field ovr) : +0.9% (1 cell)
V47 Llama pure-swap        : holdout +2 cells
```

### 5 個救不動 cells
```
BAV99W V_RRM=150     : datasheet 內 V_RRM=100
BAV99W W=2.2         : LLM H_E 2.5 差 14% 容差外
BAV99W H=1.0         : 抽 1.1 差 10% 容差外
MBR15U150 W=4.1      : 三 model + Llama 都抽 5.5
MBR15U150 H=1.2      : 三 model + Llama 都抽 4.1
```

### 失敗 iteration 教訓
```
V20 高 zoom        : vision attention 反而分散
V24 8-model vote   : 同 prompt 變種 correlated，稀釋 diverse 信號
V25 cluster vote   : 過度信任 Llama 反而傷
V29 改 prompt      : 意外影響 holdout 其他欄位
V34 verify-all     : LLM 對自己 verify 都太 confident
V36 Llama critic   : Llama 改錯 BAS16
V38 W=H_E 太寬     : 1N4148W 被誤觸傷害
V42 regex Tamb     : PyMuPDF column 抽不到 Tamb literal
V46 Llama redo     : 對 train MBR15U150 弄錯
V48 multi-sample   : ratio 2.0 trigger 太寬
```

## 文件版權 / 用途
所有檔案是 Sunny 期末作業專案的迭代紀錄。寫文章可自由引用所有數字、insight、引用本索引內提到的檔案路徑。
