"""任務四 webapp：Datasheet 參數提取系統 (V47)

跑法：
    pip install streamlit
    streamlit run app.py

兩個區塊：
  區塊一「10 顆 SPEC 示範成果」— 讀已跑好的 V47 結果，逐格對照 specbook 標答，秒出、零 API。
  區塊二「上傳 PDF 即時跑」— 端到端單模型抽取（GPT-4o + 自我檢查）+ Llama swap 偵測。
"""
import os
import sys
import json
import base64
import tempfile
from pathlib import Path

import streamlit as st

import config
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

st.set_page_config(page_title="Datasheet 參數提取系統 V47", layout="wide")

# 11 欄位的短顯示名（表頭用短名，原始長名仍是資料 key）
SHORT = {
    "Part Number": "型號",
    "Minimum Operating Temperature(°C)": "最低溫",
    "Maximum Operating Temperature (°C)": "最高溫",
    "Maximum Length (mm)": "長(mm)",
    "Maximum Width (mm)": "寬(mm)",
    "Maximum Height (mm)": "高(mm)",
    "PIN Number": "腳數",
    "I_O、I_F (A)": "電流(A)",
    "V_F(Forward Voltage) (V)": "V_F",
    "V_RRM(Peak Repetitive Reverse Voltage) (V)": "V_RRM",
    "I_R(Reverse Current) ": "I_R",
}
FIELDS = config.FIELDS
LONG_FIELDS = {"V_F(Forward Voltage) (V)", "I_R(Reverse Current) "}  # 長字串欄，顯示時截斷

L_KEY = "Maximum Length (mm)"
W_KEY = "Maximum Width (mm)"
H_KEY = "Maximum Height (mm)"


# =====================================================================
# 共用：單格對錯判斷（沿用專案統一評分邏輯）
# =====================================================================
def cell_ok(ext, exp, field):
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, exp, config.NUMERIC_TOLERANCE)
    elif field in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, exp, config.TEXT_MATCH_THRESHOLD)
        return ok
    else:
        return cmp_exact(ext, exp)


@st.cache_data
def load_demo_results():
    """讀 V47 已存結果 + specbook，算出逐格對錯。回 (rows, correct, total)。"""
    spec = load_specbook(config.SPECBOOK_PATH)
    v47 = json.loads(
        (config.ARCHIVE_DIR / "v47_llama_swap_only" / "results.json").read_text(encoding="utf-8")
    )
    rows, correct, total = [], 0, 0
    for pn, exp_rec in spec.items():
        e = v47.get(pn, {})
        cells = {}
        for f in FIELDS:
            ok = bool(cell_ok(e.get(f), exp_rec.get(f), f))
            cells[f] = {"val": e.get(f), "exp": exp_rec.get(f), "ok": ok}
            total += 1
            correct += int(ok)
        rows.append({"pn": pn, "cells": cells})
    return rows, correct, total


def _short_val(v, truncate):
    s = "" if v is None else str(v)
    if truncate and len(s) > 22:
        return s[:22] + "…", s
    return s, s


def render_demo_table(rows):
    """產生區塊一的 HTML 表格（紅底標錯格 + 標答小字）。"""
    th = "".join(
        f'<th style="padding:8px 10px;background:#f9fafb;color:#6b7280;'
        f'font-size:11.5px;text-align:left;border-bottom:1px solid #e5e7eb;'
        f'white-space:nowrap">{SHORT[f]}</th>'
        for f in FIELDS
    )
    body = ""
    for r in rows:
        tds = ""
        for i, f in enumerate(FIELDS):
            c = r["cells"][f]
            disp, full = _short_val(c["val"], f in LONG_FIELDS)
            if i == 0:
                tds += (
                    f'<td style="padding:8px 10px;font-weight:700;color:#4338ca;'
                    f'border-bottom:1px solid #e5e7eb;white-space:nowrap">{disp}</td>'
                )
            elif c["ok"]:
                tds += (
                    f'<td title="{full}" style="padding:8px 10px;border-bottom:1px solid #e5e7eb;'
                    f'white-space:nowrap;font-size:12.5px">{disp}</td>'
                )
            else:
                tds += (
                    f'<td style="padding:8px 10px;border-bottom:1px solid #e5e7eb;'
                    f'white-space:nowrap;font-size:12.5px;background:#fef2f2;color:#dc2626;'
                    f'font-weight:600">{disp}'
                    f'<span style="display:block;font-size:10.5px;opacity:.85;font-weight:400">'
                    f'標答：{c["exp"]}</span></td>'
                )
        body += f"<tr>{tds}</tr>"
    html = (
        '<div style="overflow-x:auto;border:1px solid #e5e7eb;border-radius:10px">'
        '<table style="border-collapse:collapse;width:100%;font-size:12.5px">'
        f"<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# =====================================================================
# Swap 偵測（複製自 run_v47.py，避免 import 它時觸發 module 層級設 env）
# =====================================================================
LLAMA_PROMPT = """看下方 datasheet 截圖找 Package Outline body dimensions for part {PART_NUMBER}:
- D Max = Length 軸 body
- E Max = Width 軸 body
- A Max = Height/Thickness 軸

不用 H_E/D2/E1/E2 變體。

JSON:
{{
  "D_max": <num/null>,
  "E_max": <num/null>,
  "A_max": <num/null>
}}
"""


def parse_json_lenient(text):
    text = text.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.lower().startswith("json"):
            text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    s, e = text.find("{"), text.rfind("}")
    if s == -1:
        raise ValueError
    return json.loads(text[s:e + 1])


def raster_pages(pdf_path, max_pages=6, zoom=4.5):
    import fitz
    doc = fitz.open(str(pdf_path))
    out = []
    try:
        mat = fitz.Matrix(zoom, zoom)
        for idx in range(min(doc.page_count, max_pages)):
            pix = doc[idx].get_pixmap(matrix=mat)
            out.append(base64.b64encode(pix.tobytes("png")).decode("ascii"))
    finally:
        doc.close()
    return out


def needs_redo(baseline):
    """形狀偏方（W/L>0.7 且 H/L>0.4）才值得跑 Llama 複核。"""
    try:
        l = float(baseline[L_KEY]); w = float(baseline[W_KEY]); h = float(baseline[H_KEY])
    except (TypeError, ValueError, KeyError):
        return False
    return (w / l > 0.7) and (h / l > 0.4)


def is_close(a, b, tol=0.05):
    try:
        af, bf = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if bf == 0:
        return abs(af) < 1e-6
    return abs(af - bf) / abs(bf) <= tol


def detect_pure_swap(baseline, info):
    """Llama 的 D/E 是否剛好等於 baseline 的 W/L（純對調）。不參照標準答案。"""
    cur_l, cur_w = baseline.get(L_KEY), baseline.get(W_KEY)
    new_d, new_e = info.get("D_max"), info.get("E_max")
    if cur_l is None or cur_w is None or new_d is None or new_e is None:
        return False
    return is_close(new_d, cur_w) and is_close(new_e, cur_l)


def query_llama(backend, pn, pdf_path):
    images = raster_pages(pdf_path)
    if not images:
        return {}
    raw = backend.call_multimodal(
        LLAMA_PROMPT.format(PART_NUMBER=pn), images,
        timeout=config.TIMEOUT, response_format={"type": "json_object"},
    )
    return parse_json_lenient(raw)


# =====================================================================
# 區塊二：上傳 PDF 即時端到端抽取
# =====================================================================
def run_live(pdf_path, pn):
    """端到端跑 V4 E 單模型抽取，再做 Llama swap 偵測。回 (answer, swap_info)。"""
    # V4 E 配置（與 extract_new_pdfs.py 一致）
    os.environ["BACKEND"] = "azure_gpt4o"
    os.environ["CRITIC_PROMPT_MODE"] = "conservative"
    os.environ["PDF_EXTRACTOR"] = "multimodal"
    os.environ["USE_STRICT_SCHEMA"] = "0"
    os.environ["USE_CHAIN_OF_THOUGHT"] = "0"

    from dotenv import load_dotenv
    load_dotenv()
    from llm_backend import get_backend
    from pdf_extractor import get_pdf_extractor
    from main import run_dual_agent_loop

    gpt = get_backend("azure_gpt4o")
    extractor = get_pdf_extractor("multimodal")
    text, images_b64, _ = extractor.extract_with_images(pdf_path)
    answer, _ = run_dual_agent_loop(gpt, pn, text, images_b64=images_b64, multimodal=True)

    swap_info = None
    if needs_redo(answer):
        llama = get_backend("azure_llama")
        info = query_llama(llama, pn, pdf_path)
        if detect_pure_swap(answer, info):
            before = (answer.get(L_KEY), answer.get(W_KEY))
            answer[L_KEY], answer[W_KEY] = info["D_max"], info["E_max"]
            swap_info = {"triggered": True, "before": before,
                         "llama": info, "after": (answer[L_KEY], answer[W_KEY])}
        else:
            swap_info = {"triggered": False, "llama": info}
    return answer, swap_info


def render_live_result(pn, answer, swap_info):
    st.markdown(f"#### {pn}　即時抽取結果")
    cols = st.columns(3)
    for i, f in enumerate(FIELDS):
        with cols[i % 3]:
            st.markdown(
                f'<div style="font-size:12px;color:#6b7280">{SHORT[f]}</div>'
                f'<div style="font-size:14px;font-weight:600;margin-bottom:6px">{answer.get(f)}</div>',
                unsafe_allow_html=True,
            )
    if swap_info and swap_info["triggered"]:
        b, info, a = swap_info["before"], swap_info["llama"], swap_info["after"]
        st.success(
            f"**Llama Pure Swap 觸發**　"
            f"GPT-4o 抽：長 {b[0]} / 寬 {b[1]}　→　"
            f"Llama 看圖：D {info.get('D_max')} / E {info.get('E_max')}　→　"
            f"判定純對調（誤差 <5%）→ 修正為：長 {a[0]} / 寬 {a[1]}。"
            f"\n\n此判斷只比兩個模型講法是否對調，不參照標準答案。"
        )
    elif swap_info:
        st.caption(
            f"形狀偏方、有跑 Llama 複核，但非純對調（Llama D/E="
            f"{swap_info['llama'].get('D_max')}/{swap_info['llama'].get('E_max')}），維持原值。"
        )


# =====================================================================
# 版面
# =====================================================================
st.title("Datasheet 參數提取系統　V47")
st.caption("上傳電子元件 datasheet PDF，自動抽取 11 個規格欄位。")

with st.expander("方法說明　—　對應四個任務", expanded=False):
    st.markdown(
        "**任務一　用 VLM 解析尺寸圖面**　封裝本體尺寸常只畫在 mechanical drawing 圖裡、"
        "純文字 OCR 抓不到。本系統把 PDF 頁面光柵化成圖，直接餵 GPT-4o（多模態）看圖判讀，"
        "再用 Llama vision 複核長寬是否印反。這是傳統 OCR pipeline 處理不了的圖面理解"
        "（區塊二上傳會觸發的零件可即時看到）。\n\n"
        "**任務二　強制 100% 合法 JSON（不靠 prompt）**　呼叫模型時帶 "
        "`response_format={\"type\":\"json_object\"}`（Azure / OpenAI JSON mode），"
        "本地 Ollama 帶 `format=\"json\"`，由 API 在解碼層就約束模型只能吐合法 JSON，"
        "不是在 prompt 裡拜託模型「請輸出 JSON」。所以結果能穩定進資料庫。\n\n"
        "**任務三　10 筆批次、每欄 ≥ 50%**　10 份 datasheet 全跑，總準確率 95.5%（105/110），"
        "每個欄位都遠超 50% 門檻（見下方區塊一）。\n\n"
        "**任務四　本機 webapp**　即本頁，`streamlit run app.py` 本機部署，"
        "可上傳檔案試用（區塊二）。"
    )

rows, correct, total = load_demo_results()
pct = correct / total * 100 if total else 0
with st.expander(f"①　10 顆 SPEC 示範成果　—　{pct:.1f}%　({correct}/{total} 格正確)", expanded=True):
    st.caption("讀取已跑好的結果，秒出、零 API 呼叫。紅底為與 specbook 標答不符的格子（共 5 格，皆為已知天花板）。")
    render_demo_table(rows)

st.divider()

st.subheader("②　上傳 PDF 即時跑")
st.info(
    "即時抽取為「單模型 GPT-4o 看圖 + 自我檢查 + Llama swap 偵測」版本（約 80%），"
    "非完整 8 層 V47（95.5%）。每顆約 1～2 分鐘，需 Azure 金鑰在線。"
)
files = st.file_uploader("拖曳 PDF 到這裡（可一次多檔）", type=["pdf"], accept_multiple_files=True)
if files and st.button("開始即時抽取", type="primary"):
    for f in files:
        pn = Path(f.name).stem
        with st.spinner(f"正在抽取 {f.name} … 呼叫 GPT-4o 看圖 + Llama 複核"):
            tmp = Path(tempfile.gettempdir()) / f.name
            tmp.write_bytes(f.getbuffer())
            try:
                answer, swap_info = run_live(tmp, pn)
                render_live_result(pn, answer, swap_info)
            except Exception as e:
                st.error(f"{f.name} 抽取失敗：{type(e).__name__}: {e}")
        st.divider()
