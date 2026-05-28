# V27 / V28 — Narrow re-extract 失敗實驗

## V27 — Narrow 加入 4-way vote

| 指標 | Train | Holdout | 判定 |
|---|---|---|---|
| V26 baseline | 97 = 88.2% | 100% | — |
| V27 (4-way vote) | 97 = 88.2% | 100% | **持平 — 無效** |

**為什麼無效**：narrow 1 票被 V12+V18+V22 majority outvote。例如 BAS16 W：V12=V18=V22=1.4 三票 vs narrow=2.5 一票 → 採用 1.4 (錯)。

## V28 — Narrow override on triple-agreement + 30% divergence

| 指標 | Train | Holdout | 判定 |
|---|---|---|---|
| V26 baseline | 97 = 88.2% | 100% | — |
| V28 (divergence override) | 96 = 87.3% | 100% | **退步 -1** |

**為什麼退步**：3 個 cells 被 narrow override：
- BAS16 W: 1.4 → 2.5 ✓ (對)
- 1N4148W W: 1.85 → 2.84 ✗ (錯)
- BAS21H H: 1.0 → 2.7 ✗ (錯)

淨 +1 -2 = -1。narrow 在某些 case 對 (BAS16 W vision 看清楚)，但其他 case 抽到 footprint/H_E 等變體（BAS21H H=2.7 = 含引腳高，不是 body H）。

**結論**：narrow re-extract 沒系統性提升。隨機改錯不可取。
