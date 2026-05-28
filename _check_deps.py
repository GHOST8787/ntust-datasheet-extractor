"""檢查 PDF 抽取相關依賴"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

for mod in ["camelot", "tabula", "pdfplumber", "PyPDF2", "fitz"]:
    try:
        m = __import__(mod)
        v = getattr(m, "__version__", "?")
        print(f"OK     {mod:<12} {v}")
    except ImportError:
        print(f"MISS   {mod}")
