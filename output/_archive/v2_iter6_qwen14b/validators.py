"""LLM 輸出後處理：sanity check + 自動修正

修正類型：
  - V_F：值 > 10 視為 mV 沒換算，÷1000
  - V_F / I_R：條件格式統一(去 T_J=、V_R=、dc 後綴、μ→u 等)
  - L/W/H：超出 0.2 ~ 15 mm 視為抓錯表 → null
  - 溫度：Tmin > Tmax 互換
  - PIN：非 {2, 3, 4, 8} → null
"""
import re
from typing import Dict, List, Tuple


# ===================================================================
# V_F / I_R 條件格式統一
# ===================================================================

def _normalize_condition_string(s: str) -> str:
    """
    把 V_F / I_R 字串內的條件格式統一：
      - 去掉 T_J=、TJ=、T_A=、V_R=、I_F= 等變數名(只保留值)
      - 去掉 + 前綴
      - μ / µ → u
      - 去掉 dc / ac / pk / rms 後綴
      - 條件內空白壓縮(@ 後不留空白)
      - 全形分隔保留 `、`
      - 把 `, ` (逗號+空白)當條件分隔符 → 改 `、`
      - 把 `;` 當條件分隔符 → 改 `、`
    """
    if not s or not isinstance(s, str):
        return s

    s = s.replace("μ", "u").replace("µ", "u")

    # 去 dc/ac/pk/rms 後綴(`mAdc` / `Vdc` 等)
    s = re.sub(r"(\d\s*)(mA|A|V|mV)(dc|ac|pk|rms)\b", r"\1\2", s, flags=re.IGNORECASE)
    s = re.sub(r"(\d\s*)(mA|A|V|mV)\s+(dc|ac|pk|rms)\b", r"\1\2", s, flags=re.IGNORECASE)

    # 去變數名(T_J=, TJ=, T_A=, T_C=, V_R=, V_F=, I_F=, I_R=)
    s = re.sub(r"T[_]?\s*[JjCcAa]\s*=\s*\+?", "", s)
    s = re.sub(r"V[_]?\s*[RrFf]\s*=\s*\+?", "", s)
    s = re.sub(r"I[_]?\s*[FfRrOo]\s*=\s*\+?", "", s)
    s = re.sub(r"Tj\s*=\s*\+?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"Ta\s*=\s*\+?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"Tc\s*=\s*\+?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"Tamb\s*=\s*\+?", "", s, flags=re.IGNORECASE)

    # 處理 ;  →  、
    s = s.replace(";", "、")

    # 把 ", " (逗號 + 空白)視為條目分隔(改為 、);
    # 但 "@<I>mA,<T>°C" 內逗號無空白，不會被換
    s = re.sub(r",\s+", "、", s)

    # @ 後空白壓掉
    s = re.sub(r"@\s+", "@", s)

    # 數值與單位之間空白壓掉(`5 uA` → `5uA`)
    s = re.sub(r"(\d)\s+(uA|nA|mA|A|V|mV)\b", r"\1\2", s)

    # 條件後不留多餘空白
    s = re.sub(r"\s*、\s*", "、", s)

    return s.strip()


# ===================================================================
# V_F 值 mV→V 自動換算
# ===================================================================

def _fix_vf_mv_units(s: str) -> str:
    """
    V_F 字串若值 > 10(二極體 V_F 不可能超過 ~5V)，視為 mV 沒換算 → ÷1000
    每個條目獨立判斷(BAS16 那種混雜 mV+V 的情境)
    """
    if not s or not isinstance(s, str):
        return s

    parts = re.split(r"[、]", s)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # 抓開頭數字 + 可選 mV / V 標記
        m = re.match(r"^([\d.]+)\s*(mV|V)?\s*(.*)$", p)
        if not m:
            out.append(p)
            continue
        try:
            v = float(m.group(1))
        except ValueError:
            out.append(p)
            continue
        unit_hint = (m.group(2) or "").lower()
        rest = m.group(3).strip()
        # 條件：明標 mV 或值 > 10 → ÷1000
        if unit_hint == "mv" or v > 10:
            v = v / 1000
            v_str = f"{v:g}"
            out.append(f"{v_str} {rest}".strip())
        else:
            # 已是 V，去掉 V 標記避免重複
            out.append(f"{m.group(1)} {rest}".strip())
    return "、".join(out)


# ===================================================================
# 主 validator
# ===================================================================

def validate_and_fix(rec: Dict, part_number: str) -> Tuple[Dict, List[str]]:
    """
    輸入 LLM 抽取結果與 part number，回傳修正後字典與 fix 紀錄。
    """
    fixes: List[str] = []
    if "_error" in rec:
        return rec, fixes

    # ---- 1. V_F：先 mV→V，再 format normalize ----
    vf_field = "V_F(Forward Voltage) (V)"
    if isinstance(rec.get(vf_field), str) and rec[vf_field]:
        old = rec[vf_field]
        new = _fix_vf_mv_units(old)
        new = _normalize_condition_string(new)
        if new != old:
            fixes.append(f"V_F: {old!r} → {new!r}")
            rec[vf_field] = new

    # ---- 2. I_R：format normalize (μ→u、TJ=、V_R= 等) ----
    ir_field = "I_R(Reverse Current) "
    if isinstance(rec.get(ir_field), str) and rec[ir_field]:
        old = rec[ir_field]
        new = _normalize_condition_string(old)
        if new != old:
            fixes.append(f"I_R: {old!r} → {new!r}")
            rec[ir_field] = new

    # ---- 3. L/W/H：超出 SMD 二極體合理範圍 → null ----
    for field in ["Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"]:
        v = rec.get(field)
        if isinstance(v, (int, float)) and (v > 15 or v < 0.2):
            fixes.append(f"{field}={v} 超出 0.2~15mm → null")
            rec[field] = None

    # ---- 4. 溫度：Tmin > Tmax → 互換 ----
    tmin_f = "Minimum Operating Temperature(°C)"
    tmax_f = "Maximum Operating Temperature (°C)"
    tmin = rec.get(tmin_f)
    tmax = rec.get(tmax_f)
    if isinstance(tmin, (int, float)) and isinstance(tmax, (int, float)) and tmin > tmax:
        fixes.append(f"Temp 互換：min={tmin} > max={tmax}")
        rec[tmin_f], rec[tmax_f] = tmax, tmin

    # ---- 5. PIN：必須是 2/3/4/8 ----
    pin = rec.get("PIN Number")
    if isinstance(pin, (int, float)) and int(pin) not in {2, 3, 4, 8}:
        fixes.append(f"PIN={pin} 非常見值 → null")
        rec["PIN Number"] = None

    # ---- 6. I_O/I_F：> 100 視為 mA 沒換算 → ÷1000 ----
    io_f = "I_O、I_F (A)"
    io = rec.get(io_f)
    if isinstance(io, (int, float)) and io > 100:
        new_io = io / 1000
        fixes.append(f"I_O/I_F={io} > 100A 視為 mA → {new_io}")
        rec[io_f] = new_io

    return rec, fixes
