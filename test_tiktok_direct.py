import asyncio
import os
import sys

# Them path de import tu bot.py
from tiktok_uploader import upload_to_tiktok

async def test_pipeline():
    file_path = r"C:\Users\COMPUTER\AppData\Local\CapCut\Videos\AutoPost\Hảo Huynh Đệ Sau Khi Biến Thành Nữ Sinh, Vậy Mà Chủ Động Muốn Làm Bạn Gái Cậu 《Tiểu Diệp Đồng Trú》.mp4"
    thumb_path = r"C:\Users\COMPUTER\AppData\Local\CapCut\Videos\AutoPost\Hảo Huynh Đệ Sau Khi Biến Thành Nữ Sinh, Vậy Mà Chủ Động Muốn Làm Bạn Gái Cậu 《Tiểu Diệp Đồng Trú》.png"
    
    print(f"\n2. BAT DAU UPLOAD TIKTOK CHO FILE: {file_path}")
    f = os.path.basename(file_path)
    raw_caption = os.path.splitext(f)[0]
    tiktok_caption = build_caption(raw_caption)
    
    print(f"Caption: {tiktok_caption}")
    
    
    try:
        upload_to_tiktok(file_path, tiktok_caption, thumb_path)
        print(f"==> TIKTOK UPLOAD THANH CONG: {f}")
    except Exception as e:
        print(f"==> TIKTOK UPLOAD THAT BAI: {e}")

if __name__ == "__main__":
    # Fix unicode print on Windows console
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    asyncio.run(test_pipeline())
