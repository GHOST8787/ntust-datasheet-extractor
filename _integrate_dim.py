"""整合:把裁切版尺寸抽取(crop2 邏輯)的 L/W/H 替換進 V23，跑完整 110 格，印確切整體分數 + 逐欄。
不估計，實跑。容差與 evaluate_all 一致(numeric ±5%)。
"""
import os, sys, json, base64, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
os.environ["BACKEND"] = "azure_gpt4o"
from dotenv import load_dotenv
load_dotenv()
import fitz
import config
from llm_backend import get_backend
from reevaluate import cmp_numeric, cmp_exact, cmp_text, load_specbook
import crop_extractor

ORIG_KW = list(crop_extractor.CROP_ANCHOR_KEYWORDS)
backend = get_backend("azure_gpt4o")
DIM_FIELDS = ["Maximum Length (mm)", "Maximum Width (mm)", "Maximum Height (mm)"]


def raster_full(pdf_path, zoom=5.0, maxp=6):
    doc = fitz.open(str(pdf_path))
    out = []
    mat = fitz.Matrix(zoom, zoom)
    for i in range(min(doc.page_count, maxp)):
        out.append(base64.b64encode(doc[i].get_pixmap(matrix=mat).tobytes("png")).decode("ascii"))
    doc.close()
    return out


def crops_default(pdf):
    crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW
    return crop_extractor.get_dimension_crops(pdf, zoom=6.0, max_crops=3)


def crops_extended(pdf):
    crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW + ["DIMENSIONS", "Dimensions"]
    try:
        return crop_extractor.get_dimension_crops(pdf, zoom=6.0, max_crops=3)
    finally:
        crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW


PROMPT = """看 datasheet 截圖的 Package Outline / Mechanical Dimensions / DIMENSIONS 表
(不是 Land Pattern / Footprint / Suggested Solder Pad / Tape),抽這顆零件的「最大外形尺寸」。

# 關鍵定義(通用,適用所有封裝)
- **Maximum Length / Maximum Width = 含引腳的最大外形尺寸(overall, lead-to-lead span)**,不是 body 本體尺寸。
  - 例:SOT-23 的 E(lead span ~2.5)是含引腳外形,E1(body ~1.3)是本體 → Width 取 E 那個含引腳的較大值。
  - 表中若同時有 body 符號與含引腳符號(如 E vs E1、或 D vs H_E / lead span),取「含引腳/外形較大」那個。
- **Maximum Height = 封裝總高**(常見符號 A,也可能標成 T 或 H)。
- 三個值都取該列的 **MAX 欄(最右/最大)**,不是 MIN / NOM / TYP。
- **若尺寸標成「中心值 ± 公差」格式(例如 1.55±0.1),Max = 中心值 + 公差(=1.65),不要只取中心值。**
- Length 取較長軸方向、Width 取較短軸方向的含引腳外形(依圖示方向)。
- 單位若為 inch,乘 25.4。

# 輸出 JSON
{{"Maximum Length (mm)": <數值或null>, "Maximum Width (mm)": <數值或null>, "Maximum Height (mm)": <數值或null>}}
只輸出 JSON。"""


def parse(t):
    t = t.strip()
    m = re.search(r"\{.*\}", t, re.DOTALL)
    return json.loads(m.group(0)) if m else {}


def extract_dims(pdf_fn):
    pdf = config.DATASHEETS_DIR / pdf_fn
    crops = crops_default(pdf)
    if not crops:
        crops = crops_extended(pdf)
    imgs = [b64 for _, b64 in crops] if crops else raster_full(pdf)
    try:
        ans = parse(backend.call_multimodal(PROMPT, imgs, timeout=config.TIMEOUT))
    except Exception:
        ans = {}
    return {f: ans.get(f) for f in DIM_FIELDS}


def cell_correct(extracted, exp_rec, field):
    ext = extracted.get(field)
    exp = exp_rec.get(field)
    if field in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, exp, config.NUMERIC_TOLERANCE)
    elif field in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, exp, config.TEXT_MATCH_THRESHOLD)
        return ok
    else:
        return cmp_exact(ext, exp)


# --- 載 V23 + 替換尺寸三欄 ---
spec = load_specbook(config.SPECBOOK_PATH)
v23_path = config.ARCHIVE_DIR / "v23_majority_vote_3model" / "results.json"
v23 = json.loads(v23_path.read_text(encoding="utf-8"))

print("整合:把裁切版尺寸抽取替換進 V23 ...\n", flush=True)
merged = {}
for pn, pdf_fn in config.PART_TO_PDF.items():
    rec = {k: v for k, v in dict(v23.get(pn, {})).items() if not k.startswith("_")}
    dims = extract_dims(pdf_fn)
    for f in DIM_FIELDS:
        rec[f] = dims[f]
    merged[pn] = rec
    print(f"  [{pn}] L={dims[DIM_FIELDS[0]]}  W={dims[DIM_FIELDS[1]]}  H={dims[DIM_FIELDS[2]]}", flush=True)

# 存整合結果
out_dir = config.ARCHIVE_DIR / "v_clean_dim_integrated"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "results.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

# --- 評估全 110 格 ---
correct = 0
total = 0
per_field_ok = {f: 0 for f in config.FIELDS}
per_field_total = {f: 0 for f in config.FIELDS}
for pn, exp_rec in spec.items():
    e = merged.get(pn, {})
    for f in config.FIELDS:
        total += 1
        per_field_total[f] += 1
        if cell_correct(e, exp_rec, f):
            correct += 1
            per_field_ok[f] += 1

print(f"\n=== 整合後完整 110 格(零 overfit:三模型投票 + 裁切尺寸抽取)===", flush=True)
print(f"整體: {correct}/{total} = {correct/total*100:.1f}%   (V23 原本 96/110 = 87.3%)\n", flush=True)
print("逐欄位正確率(對照作業 60% 門檻):", flush=True)
for f in config.FIELDS:
    ok = per_field_ok[f]
    tot = per_field_total[f]
    pct = ok / tot * 100
    flag = "" if pct >= 60 else "  <-- 未過 60%"
    print(f"  {ok:2d}/{tot} = {pct:5.1f}%  {f}{flag}", flush=True)
