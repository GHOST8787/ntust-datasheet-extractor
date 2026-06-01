"""整合:裁切 + 四條規則 + 多次取多數(self-consistency)版尺寸,替換進 V23,跑完整 110 格。
零 overfit。不估,實跑。
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
N_SAMPLES = 5


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
    return crop_extractor.get_dimension_crops(pdf, zoom=6.0, max_crops=2)


def crops_extended(pdf):
    crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW + ["DIMENSIONS", "Dimensions"]
    try:
        return crop_extractor.get_dimension_crops(pdf, zoom=6.0, max_crops=2)
    finally:
        crop_extractor.CROP_ANCHOR_KEYWORDS = ORIG_KW


PROMPT = """看 datasheet 截圖的 Package Outline / Mechanical Dimensions / DIMENSIONS 表,抽這顆零件的「最大外形尺寸」長/寬/高。

# 通用規則(適用所有封裝,每條都要檢查)
1. 三個值都取規格表的 Max 欄(最右/最大),不要取 Min / Nom / Typ。
2. 【±公差】尺寸若寫成「中心值 ± 公差」(例如 0.9±0.1、1.55±0.1),你回報的值必須是 中心值＋公差(0.9±0.1→1.0、1.55±0.1→1.65)。先算「中心＋公差」再報,絕不只報中心值。
3. 【含引腳取大】Length / Width 要的是「含引腳的最大外形」(lead-to-lead overall),不是本體。同一個方向若表上有多個候選符號(本體 vs 含引腳,例如 D 本體長 vs H 含引腳全長、E 本體 vs lead span),一律取「數值較大」的那個。
4. 【字母不代表軸】符號字母(A / D / E / H / L…)不代表它量哪個軸——不要看到「H」就當高度、看到「D」就當長度。要依圖上標註線的指向判斷它量的是哪個方向。
5. 【高度合理性檢查】這類扁平 SMD 封裝的高度(厚度)幾乎一定是長、寬、高三者中「最小」的。若你選出來的高度比長度或寬度還大,代表選錯了——回去重判哪個符號才是垂直厚度方向。
6. 【排除非本體表】只抽封裝本體尺寸表;不要抽 Carrier Tape(包裝載帶)、Land Pattern / Recommended Footprint(焊墊)的數字。
7. 單位若為 inch,乘 25.4。

# 輸出 JSON
{{"Maximum Length (mm)": <數值或null>, "Maximum Width (mm)": <數值或null>, "Maximum Height (mm)": <數值或null>}}
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
    crops = crops_default(pdf) or crops_extended(pdf)
    imgs = [b64 for _, b64 in crops] if crops else raster_full(pdf)
    samples = {f: [] for f in DIM_FIELDS}
    for _ in range(N_SAMPLES):
        try:
            ans = parse(backend.call_multimodal(PROMPT, imgs, timeout=config.TIMEOUT))
        except Exception:
            continue
        for f in DIM_FIELDS:
            samples[f].append(ans.get(f))
    return {f: majority(samples[f]) for f in DIM_FIELDS}


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

print(f"整合:裁切 + 四條規則 + 多次取多數 x{N_SAMPLES} 版尺寸 替換進 V23 ...\n", flush=True)
merged = {}
for pn, pdf_fn in config.PART_TO_PDF.items():
    rec = {k: v for k, v in dict(v23.get(pn, {})).items() if not k.startswith("_")}
    dims = extract_dims(pdf_fn)
    for f in DIM_FIELDS:
        rec[f] = dims[f]
    merged[pn] = rec
    print(f"  [{pn}] L={dims[DIM_FIELDS[0]]}  W={dims[DIM_FIELDS[1]]}  H={dims[DIM_FIELDS[2]]}", flush=True)

out_dir = config.ARCHIVE_DIR / "v_clean_dim_rules_sc_integrated"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "results.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

correct = 0
per_field = {}
for pn, exp in spec.items():
    for f in config.FIELDS:
        ok = cell_correct(merged.get(pn, {}), exp, f)
        correct += int(ok)
        per_field[f] = per_field.get(f, 0) + int(ok)

print(f"\n=== 整合後完整 110 格(零 overfit:三模型投票 + 裁切 + 四條規則 + 多次取多數)===", flush=True)
print(f"整體: 110 格對 {correct} 格\n", flush=True)
for f in config.FIELDS:
    print(f"  10 格對 {per_field[f]} 格  {f}", flush=True)
