r"""V2 打包腳本

產出 Desktop\20260510_期末作業_V2.zip,包含:
  - 6 個 .py 主檔
  - requirements.txt / README.md / AZURE_SETUP.md / .env.example
  - data/ datasheets/
  - output/results_v2.xlsx + results.json + _archive/(完整 7 cell + 報告)
  - C:\Users\sunny\Downloads\20260510_V2.docx(交作業文件)

排除:
  - .env(API key 安全)
  - __pycache__ / _check_deps.py / _test_azure.py / 0508.pptx / _make_zip.py(自己)
"""
import os
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT = Path(__file__).resolve().parent
DOCX = Path(r"C:\Users\sunny\Downloads\20260510_V2.docx")
OUT_ZIP = Path(r"C:\Users\sunny\Desktop\20260510_期末作業_V2.zip")
ROOT_NAME = "20260510_期末作業_V2"  # zip 內最外層資料夾名稱

# 排除規則
EXCLUDE_FILES = {
    ".env",
    "_check_deps.py",
    "_test_azure.py",
    "_make_zip.py",
    "0508.pptx",
}
EXCLUDE_DIR_NAMES = {"__pycache__", "v1_extract"}


def should_skip(rel: Path) -> bool:
    """判斷某相對路徑要不要排除"""
    parts = rel.parts
    if rel.name in EXCLUDE_FILES:
        return True
    # Office 開啟中的 lock 檔(~$xxx.docx)
    if rel.name.startswith("~$"):
        return True
    for d in EXCLUDE_DIR_NAMES:
        if d in parts:
            return True
    return False


def main():
    if not DOCX.exists():
        print(f"[WARN] 找不到 {DOCX}")
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()

    count = 0
    skip = 0
    total_size = 0
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1. 專案主目錄遞迴打包
        for path in PROJECT.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(PROJECT)
            if should_skip(rel):
                skip += 1
                continue
            arcname = f"{ROOT_NAME}/{rel.as_posix()}"
            zf.write(path, arcname)
            count += 1
            total_size += path.stat().st_size

        # 2. 加 docx(交作業文件,放 zip 根)
        if DOCX.exists():
            arcname = f"{ROOT_NAME}/{DOCX.name}"
            zf.write(DOCX, arcname)
            count += 1
            total_size += DOCX.stat().st_size
            print(f"  + 加入 {DOCX.name}")

    out_size_mb = OUT_ZIP.stat().st_size / 1024 / 1024
    src_size_mb = total_size / 1024 / 1024
    print()
    print(f"=== 打包完成 ===")
    print(f"路徑: {OUT_ZIP}")
    print(f"檔案數: {count}(跳過 {skip} 個排除項)")
    print(f"原始大小: {src_size_mb:.2f} MB")
    print(f"壓縮後: {out_size_mb:.2f} MB")
    print(f"壓縮率: {(1 - out_size_mb / src_size_mb) * 100:.0f}%")


if __name__ == "__main__":
    main()
