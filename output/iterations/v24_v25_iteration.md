# V24 & V25 — 兩個失敗實驗

## V24 — 擴大池到 8 model

| 指標 | Train | Holdout | 判定 |
|---|---|---|---|
| V23 baseline | 94 = 85.5% | 100% | — |
| V24 (V10/V11/V12/V14/V15/V17/V18/V22) | 93 = 84.5% | 100% | **退步 -1** |

**失敗原因**：V10/V11/V12/V14/V15/V17 都是 GPT-4o conservative 同 prompt 變種，他們的 errors **高度 correlated**。加進池後**稀釋了 V18 + V22 的 differential 信息**，反而傷害 V23 的突破效果。

**結論**：multi-model vote 要 **diverse**（不同 model architecture / 不同 prompt structure），不是「越多越好」。

## V25 — Cluster-aware vote (平手時 prefer V18)

| 指標 | Train | Holdout | 判定 |
|---|---|---|---|
| V23 baseline | 94 = 85.5% | 100% | — |
| V25 (cluster vote) | 93 = 84.5% | 100% | **退步 -1** |

**失敗原因**：V18 對 V12==V22 不同的 cells 中，**只有 ~3/14 真的 V18 對**（CD4148WTP 三軸），其餘 V12+V22 才是對的。「平手 prefer V18」反而引入更多錯誤。

## 學到的 generic 規則（後續 V26 用到）

對 V12==V22≠V18 conflicts：
- 大部分 cell V12+V22 對（GPT-4o family 更可靠）
- 但**triaxis 全部** V12==V22≠V18 的 part = small package vision arch bias → V18 vision 更準

→ V26 = 用 triaxis 全部 isolation 當 trigger。
