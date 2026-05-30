# OVERFIT 逐版判定（2026-05-28 audit）

## 標準（評分集只有 10 份 spec）
評分集只有 10 份 datasheet（specbook.xlsx），這 10 份即評分集本身，沒有 train/test 之分。
**算 overfit**：任何「知道這 10 份特定答案後才寫出來的」邏輯 —— 寫死值、門檻逐顆反推、規則點名某顆 part、或範例照這 10 份錯誤型態做。
**不算 overfit**：通用領域規則（JEDEC D=長度、取 MAX 欄、單位換算）、多模型投票、換模型/截圖/extractor、用不算分的外部 datasheet 當 few-shot。

## 乾淨（未標記，任何尺度都站得住）
V1-V9、V14、V17-V24、V27、V28。其中分數最高：V23 三模型投票約 85.5%。

## 已標記 OVERFIT（含可疑層，最嚴格尺度）
| 版本 | 原因 |
|---|---|
| V10 | prompt 步驟2.5 加入 DPAK/D2PAK 具體尺寸範例（取自不算分的 AA 5 份；最嚴格尺度下視為可疑） |
| V11 | prompt 加入 explicit FFSH5065B 尺寸範例 |
| V12 | prompt 步驟3.6 完整尺寸範例（FFSH5065B / FFSD1065B） |
| V13 | 反例 5-8 照 DFLS160 / CD4148WTP / MBR15U150 / BAV99W 的錯誤型態做（退步未採用） |
| V15 | strict critic 為救 CD4148WTP 而調 |
| V16 | hybrid critic 點名 CD4148WTP / BAS21H / BAV99W / DFLS160 |
| V25 | cluster-aware 投票邏輯微調（輕微可疑） |
| V26 | triaxis override 由 CD4148WTP 一顆觀察推導 |
| V29 | prompt 反推 BAV99W=150、1N4148W=0.15 等特定答案 |
| V30 | V29+V26 組合，繼承 V29 的答案調校 |
| V31 | 只 override 2 欄；override 範圍是依這 10 份哪幾格被修而選的（界線版，專案自稱 generic 天花板） |
| V32 | 建在 V31，Tj regex 後處理 |
| V33 | 建在 V31，Tj LLM query 後處理 |
| V34 | 建在 V31，verify critic |
| V35 | 4-way vote 含 V29 |
| V36 | 建在 V31，Llama critic |
| V37 | L=max(D,E) 規則來自『10/10 spec 都 L>=W』統計，直接擬合評分集 |
| V38 | W H_E override，part-specific |
| V39 | L outer override 為救 BAS21H |
| V40 | ratio 門檻逐顆反推（BAS16 1.79 / BAV99W 1.76 trigger，1N4148W 2.09 排除） |
| V41 | Tj rule 為救 BAV99W、避開 BAS16 |
| V42 | Tj regex Tamb，part-specific |
| V43 | H_E rule for BAV99W，ratio 1.4~1.8 反推排除 1N4148W |
| V44 | Tj grep Tamb 精準區分 BAV99W vs BAS16（95.5% 來源） |
| V45 | WH 重抽針對 MBR15U150 |
| V46 | Llama WH 針對 MBR15U150 |
| V47 | part-specific 門檻 + 對 AA 5 份其中一顆（VS3C12ET07S2L）調；final，最嚴重 |
| V48 | ratio 放寬到剛好含 BAV99W=1.92 |

## 建議交件
- 最安全：**V23（85.5%）**，純通用手法。
- 想衝高且可辯護：**V31（89.1%）**，但報告須註明「89.1% 是不加 part-specific 規則的上限；V37 起的 95.5% 是擬合這 10 份的結果，不代表泛化」。
- **不要**把 V44（95.5%）或 V47 當「不 overfit」的成績交出。

## 注意
- `REPORT.docx` 未自動更動，需從更正後的 `REPORT.md` 重新產生。
- `output/iteration_logs/*_NEW_PDFS_test/` 為中間測試 log，本次未標。
