"""PoC:視覺增強(set-of-mark)。在 DFLS160 機構圖上用程式畫出標註線方向
(水平線=紅、垂直線=藍,排除表格超長框線),再給 VLM 看這張標好方向的圖判長寬。
看 VLM 用「畫好方向」的圖能否穩定判對寬度(GT 1.93,平常 VLM 抽成本體 3.0)。
"""
import os, sys, json, base64, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
os.environ["BACKEND"] = "azure_gpt4o"
from dotenv import load_dotenv
load_dotenv()
import fitz
import config
from llm_backend import get_backend

backend = get_backend("azure_gpt4o")
pdf = config.DATASHEETS_DIR / config.PART_TO_PDF["DFLS160"]
doc = fitz.open(str(pdf))
page = doc[3]  # Package Outline 頁

# 偵測中等長度線(排除超長表格框 >200),在頁上畫色:水平紅、垂直藍
nh = nv = 0
for d in page.get_drawings():
    r = d["rect"]
    w, h = r.width, r.height
    if 15 < w < 200 and h < 3:  # 水平標註線
        y = (r.y0 + r.y1) / 2
        page.draw_line((r.x0, y), (r.x1, y), color=(1, 0, 0), width=2.0)
        nh += 1
    elif 15 < h < 200 and w < 3:  # 垂直標註線
        x = (r.x0 + r.x1) / 2
        page.draw_line((x, r.y0), (x, r.y1), color=(0, 0, 1), width=2.0)
        nv += 1

print(f"畫了 水平紅線 {nh} 條 / 垂直藍線 {nv} 條\n", flush=True)

# raster 成增強 PNG
pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0))
b64 = base64.b64encode(pix.tobytes("png")).decode("ascii")
# 存一份供檢視
(config.OUTPUT_DIR / "_dfls160_marked.png").write_bytes(pix.tobytes("png"))
doc.close()

PROMPT = """這張封裝機構圖上,我用顏色標了標註線的方向:
- 紅線 = 橫向(水平)方向的尺寸標註
- 藍線 = 縱向(垂直)方向的尺寸標註
請依顏色判斷方向,抽最大外形尺寸:
- Maximum Length = 橫向(紅線方向)含引腳的最大尺寸
- Maximum Width = 縱向(藍線方向)的最大尺寸
- Maximum Height = 封裝厚度(三維中最小那個)
配規格表的 Max 值(每列取最大);若 X±Y 取 X+Y;inch 乘 25.4。
輸出 JSON:{{"Maximum Length (mm)": <>, "Maximum Width (mm)": <>, "Maximum Height (mm)": <>}}
只輸出 JSON。"""


def parse(t):
    t = t.strip()
    m = re.search(r"\{.*\}", t, re.DOTALL)
    return json.loads(m.group(0)) if m else {}


GT = {"Maximum Length (mm)": 3.9, "Maximum Width (mm)": 1.93, "Maximum Height (mm)": 1.0}
print("跑 3 次看穩定度:\n", flush=True)
for i in range(3):
    try:
        ans = parse(backend.call_multimodal(PROMPT, [b64], timeout=config.TIMEOUT))
    except Exception as ex:
        print(f"  run{i+1} FAIL: {ex}", flush=True)
        continue
    parts = []
    for f, k in [("Maximum Length (mm)", "L"), ("Maximum Width (mm)", "W"), ("Maximum Height (mm)", "H")]:
        v = ans.get(f)
        ok = v is not None and abs(v - GT[f]) <= GT[f] * 0.05
        parts.append(f"{k}={'OK' if ok else 'X'}({v}/{GT[f]})")
    print(f"  run{i+1}: {'  '.join(parts)}", flush=True)
