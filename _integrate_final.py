"""最終定案整合(零 overfit):
- 尺寸:裁切 + 四條通用規則 + 多次取多數(self-consistency)
- 電流 I_O/I_F 欄:看 Maximum Ratings 表,優先取 I_O(平均整流輸出電流)+ 多次取多數
- 其他欄:V23 三模型投票
跑完整 110 格,印整體 + 逐欄 + 剩餘錯格明細。
"""
import os, sys, json, base64, re
from collections import Counter
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
CUR = "I_O、I_F (A)"
N = 5
NC = 3


def raster(pdf_path, zoom=5.0, maxp=6, start=0):
    doc = fitz.open(str(pdf_path))
    out = []
    mat = fitz.Matrix(zoom, zoom)
    for i in range(start, min(doc.page_count, start + maxp)):
        out.append(base64.b64encode(doc[i].get_pixmap(matrix=mat).tobytes("png")).decode("ascii"))
    doc.close()
    return out


def crops(pdf):
    crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW
    c = crop_extractor.get_dimension_crops(pdf, zoom=6.0, max_crops=2)
    if not c:
        crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW + ["DIMENSIONS", "Dimensions"]
        c = crop_extractor.get_dimension_crops(pdf, zoom=6.0, max_crops=2)
        crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW
    return c


DIM_PROMPT = """看 datasheet 截圖的 Package Outline / Mechanical Dimensions / DIMENSIONS 表,抽「最大外形尺寸」長/寬/高。
# 通用規則
1. 取規格表 Max 欄(最大),不取 Min/Nom/Typ。
2. X±Y 格式 → 取 X+Y(如 0.9±0.1→1.0)。
3. Length/Width 取「含引腳的最大外形」,不取本體;同方向有本體與含引腳兩符號時取較大的。
4. 符號字母不代表軸,別看到 H 就當高度,依標註線方向判斷。
5. 扁平 SMD 高度幾乎是長寬高三者最小;若高度比長或寬還大就是選錯,重判。
6. 只抽封裝本體尺寸表,排除 Carrier Tape / Land Pattern / Footprint。
7. inch 乘 25.4。
輸出 JSON:{{"Maximum Length (mm)": <>, "Maximum Width (mm)": <>, "Maximum Height (mm)": <>}}
只輸出 JSON。"""

CUR_PROMPT = """看 datasheet 的 Maximum Ratings / Absolute Maximum Ratings 表,抽額定順向電流。
此欄優先取「平均整流輸出電流 I_O」(Average Rectified Output/Forward Current,符號 IO 或 IF(AV));
只有當這份 datasheet 完全沒有平均整流電流時,才取「連續/峰值順向電流 I_F / IFM / IFRM」。
數值若單位是 mA,除以 1000 換成 A。
輸出 JSON:{{"value": <數值,單位A>}}
只輸出 JSON。"""


def parse(t):
    t = t.strip()
    m = re.search(r"\{.*\}", t, re.DOTALL)
    return json.loads(m.group(0)) if m else {}


def majority(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    c = Counter(str(v) for v in vals)
    top = c.most_common(1)[0][0]
    for v in vals:
        if str(v) == top:
            return v
    return vals[0]


def extract_dims(pdf_fn):
    pdf = config.DATASHEETS_DIR / pdf_fn
    c = crops(pdf)
    imgs = [b64 for _, b64 in c] if c else raster(pdf, maxp=6)
    s = {f: [] for f in DIM_FIELDS}
    for _ in range(N):
        try:
            a = parse(backend.call_multimodal(DIM_PROMPT, imgs, timeout=config.TIMEOUT))
        except Exception:
            continue
        for f in DIM_FIELDS:
            s[f].append(a.get(f))
    return {f: majority(s[f]) for f in DIM_FIELDS}


def extract_current(pdf_fn):
    pdf = config.DATASHEETS_DIR / pdf_fn
    imgs = raster(pdf, maxp=3)  # Maximum Ratings 通常在前幾頁
    vals = []
    for _ in range(NC):
        try:
            a = parse(backend.call_multimodal(CUR_PROMPT, imgs, timeout=config.TIMEOUT))
            vals.append(a.get("value"))
        except Exception:
            continue
    return majority(vals)


def cell_correct(e, exp, f):
    ext, expv = e.get(f), exp.get(f)
    if f in config.NUMERIC_FIELDS:
        return cmp_numeric(ext, expv, config.NUMERIC_TOLERANCE)
    elif f in config.TEXT_FIELDS:
        ok, _ = cmp_text(ext, expv, config.TEXT_MATCH_THRESHOLD)
        return ok
    return cmp_exact(ext, expv)


spec = load_specbook(config.SPECBOOK_PATH)
v23 = json.loads((config.ARCHIVE_DIR / "v23_majority_vote_3model" / "results.json").read_text(encoding="utf-8"))

print("最終整合(尺寸 rules+sc / 電流 IO優先+sc / 其他 V23)...\n", flush=True)
merged = {}
for pn, pdf_fn in config.PART_TO_PDF.items():
    rec = {k: v for k, v in dict(v23.get(pn, {})).items() if not k.startswith("_")}
    dims = extract_dims(pdf_fn)
    for f in DIM_FIELDS:
        rec[f] = dims[f]
    rec[CUR] = extract_current(pdf_fn)
    merged[pn] = rec
    print(f"  [{pn}] L={dims[DIM_FIELDS[0]]} W={dims[DIM_FIELDS[1]]} H={dims[DIM_FIELDS[2]]} 電流={rec[CUR]}", flush=True)

out_dir = config.ARCHIVE_DIR / "v_final_integrated"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "results.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

correct = 0
per_field = {}
errs = []
for pn, exp in spec.items():
    for f in config.FIELDS:
        ok = cell_correct(merged.get(pn, {}), exp, f)
        correct += int(ok)
        per_field[f] = per_field.get(f, 0) + int(ok)
        if not ok:
            errs.append((pn, f, merged.get(pn, {}).get(f), exp.get(f)))

print(f"\n=== 定案:110 格對 {correct} 格 ===\n", flush=True)
for f in config.FIELDS:
    print(f"  10 格對 {per_field[f]} 格  {f}", flush=True)
print(f"\n剩餘錯格 {len(errs)} 個(抽/答):", flush=True)
for pn, f, ext, exp in errs:
    print(f"  [{pn}] {f}: 抽 {ext} / 答 {exp}", flush=True)
