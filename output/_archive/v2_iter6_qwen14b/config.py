"""V2 全域設定：路徑、模型、欄位、Part Number → PDF 對應"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATASHEETS_DIR = PROJECT_ROOT / "datasheets"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
SPECBOOK_PATH = DATA_DIR / "specbook.xlsx"

# Ollama 本地推理（資料不上雲）
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:14b"
TEMPERATURE = 0.0
NUM_CTX = 16384
TIMEOUT = 600
MAX_RETRIES = 3

# PDF 抽取參數
MAX_PDF_PAGES = 10
MAX_PDF_CHARS = 12000  # 預留 LLM context 給 prompt template + self-check
PDF_KEYWORDS = [
    # Temperature
    "Operating", "Temperature", "Junction", "Tj", "Tamb",
    # Dimensions
    "Dimension", "Package", "Outline", "Mechanical", "Drawing",
    # Pin
    "Pin", "Marking", "Lead",
    # Currents
    "Forward Current", "Average", "I_F", "I_O", "Continuous",
    # V_F
    "Forward Voltage", "V_F",
    # V_RRM
    "Reverse Voltage", "V_RRM", "V_R", "Peak",
    # I_R
    "Reverse Current", "I_R", "Leakage",
    # Section headings
    "Absolute Maximum", "Electrical Characteristics", "Ratings", "Symbol", "Parameter",
    # Inch unit hint
    "inch", "inches",
]

# Part Number → PDF 檔名對應（用 specbook 的 Part Number 對 datasheets/ 內 PDF 名稱比對得出）
PART_TO_PDF = {
    "1N4148W":     "1N4148W N0571 REV.E.pdf",
    "BAS16":       "BAS16.pdf",
    "BAS21H":      "BAS21HT1-D.pdf",
    "BAT750":      "BAT750.pdf",
    "BAV99W":      "BAV99W_datasheet_en_20171221.pdf",
    "CD4148WTP":   "CD4148WTP.pdf",
    "DFLS160":     "DFLS160.pdf",
    "MBR15U150":   "MBR15U150(TO-277).pdf",
    "MSB30M":      "MSB30M.pdf",
    "SBR05U20LPS": "SBR05U20LPS.pdf",
}

# 11 個欄位（與 specbook.xlsx 標題列完全一致，含特殊字元）
FIELDS = [
    "Part Number",
    "Minimum Operating Temperature(°C)",
    "Maximum Operating Temperature (°C)",   # ( 前有 1 個空白
    "Maximum Length (mm)",
    "Maximum Width (mm)",
    "Maximum Height (mm)",
    "PIN Number",
    "I_O、I_F (A)",                          # 全形頓號
    "V_F(Forward Voltage) (V)",
    "V_RRM(Peak Repetitive Reverse Voltage) (V)",
    "I_R(Reverse Current) ",                 # 尾端有 1 個空白
]

NUMERIC_FIELDS = {
    "Minimum Operating Temperature(°C)",
    "Maximum Operating Temperature (°C)",
    "Maximum Length (mm)",
    "Maximum Width (mm)",
    "Maximum Height (mm)",
    "I_O、I_F (A)",
}
EXACT_FIELDS = {
    "Part Number",
    "V_RRM(Peak Repetitive Reverse Voltage) (V)",
    "PIN Number",
}
TEXT_FIELDS = {
    "V_F(Forward Voltage) (V)",
    "I_R(Reverse Current) ",
}

# 比對閾值
NUMERIC_TOLERANCE = 0.05      # 數值欄位 ±5%
TEXT_MATCH_THRESHOLD = 0.5    # V_F / I_R token 集合命中率
