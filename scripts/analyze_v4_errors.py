"""V4 E 錯誤分析：把 23 格錯按欄位 / 錯誤類型分類，找最大頭

讀 V4 E 的 errors_detail.json，輸出：
1. 按欄位統計：哪個欄位錯最多？
2. 按元件統計：哪顆元件錯最多？
3. 每格錯的具體 expected vs extracted
4. 錯誤類型分類（值近但超容差 / 漏抓 / 取錯欄 / 真未知）
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import config

ARCHIVE = config.ARCHIVE_DIR / "v4_multimodal_azure_gpt_4o_conservative"
errors = json.loads((ARCHIVE / "errors_detail.json").read_text(encoding="utf-8"))

print(f"V4 E 總共 {len(errors)} 格錯")
print()

# ===== 按欄位統計 =====
by_field = defaultdict(list)
for e in errors:
    by_field[e["field"]].append(e)

print("=== 按欄位統計 ===")
print(f"{'Field':<55} {'Count':>5}")
for f, lst in sorted(by_field.items(), key=lambda x: -len(x[1])):
    print(f"{f:<55} {len(lst):>5}")
print()

# ===== 按元件統計 =====
by_part = defaultdict(list)
for e in errors:
    by_part[e["part"]].append(e)

print("=== 按元件統計 ===")
print(f"{'Part':<15} {'Errors':>7}")
for p, lst in sorted(by_part.items(), key=lambda x: -len(x[1])):
    print(f"{p:<15} {len(lst):>7}")
print()

# ===== 每格錯的具體內容 =====
print("=== 每格錯的具體 expected vs extracted ===")
for e in errors:
    print(f"\n[{e['part']}] {e['field']}")
    print(f"  expected:  {e['expected']!r}")
    print(f"  extracted: {e['extracted']!r}")
print()


# ===== 錯誤類型分類 =====
def classify(e):
    exp = e["expected"]
    ext = e["extracted"]
    if ext == "" or ext == "None" or ext is None:
        return "missing_value"
    # 試 numeric 邊緣
    try:
        ef = float(exp)
        xf = float(ext)
        diff_pct = abs(xf - ef) / max(abs(ef), 1e-6)
        if diff_pct < 0.15:
            return "numeric_borderline"  # 差 < 15% 但超 5% 容差
        elif diff_pct < 0.5:
            return "numeric_wrong"  # 差 15-50%
        else:
            return "numeric_very_wrong"
    except (ValueError, TypeError):
        pass
    # 字串：看 V_F / I_R 多條件
    if "@" in str(exp) or "@" in str(ext):
        exp_conditions = len(re.split(r"[、]", str(exp)))
        ext_conditions = len(re.split(r"[、]", str(ext)))
        if abs(exp_conditions - ext_conditions) >= 1:
            return "multi_condition_string_count"
        else:
            return "multi_condition_string_content"
    return "string_other"


print("=== 錯誤類型分類 ===")
classified = defaultdict(list)
for e in errors:
    cls = classify(e)
    classified[cls].append(e)

for cls, lst in sorted(classified.items(), key=lambda x: -len(x[1])):
    print(f"\n--- {cls}: {len(lst)} 格 ---")
    for e in lst:
        print(f"  [{e['part']:<15}] {e['field'][:35]:<35} | {e['expected'][:30]:>30} != {e['extracted'][:30]}")
