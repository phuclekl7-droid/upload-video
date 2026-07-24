import asyncio
import os
import sys

# Them path de import tu bot.py
sys.path.append(r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster")
import video_tools
from bot import run_uploader, build_caption

async def test_pipeline():
    original_video = r"C:\Users\COMPUTER\AppData\Local\CapCut\Videos\AutoPost\Hảo Huynh Đệ Sau Khi Biến Thành Nữ Sinh, Vậy Mà Chủ Động Muốn Làm Bạn Gái Cậu 《Tiểu Diệp Đồng Trú》 Tập 1-14.mp4"
    thumb_path = r"C:\Users\COMPUTER\AppData\Local\CapCut\Videos\AutoPost\Hảo Huynh Đệ Sau Khi Biến Thành Nữ Sinh, Vậy Mà Chủ Động Muốn Làm Bạn Gái Cậu 《Tiểu Diệp Đồng Trú》16 9.png"
    
    print("1. BAT DAU CAT VIDEO...")
    try:
        split_files = video_tools.split_video(original_video, 2)
        print(f"Da cat thanh {len(split_files)} phan: {split_files}")
    except Exception as e:
        print(f"LOI CAT VIDEO: {e}")
        return

    for file_path in split_files:
        print(f"\n2. BAT DAU UPLOAD TIKTOK CHO FILE: {file_path}")
        f = os.path.basename(file_path)
        raw_caption = os.path.splitext(f)[0]
        tiktok_caption = build_caption(raw_caption)
        
        print(f"Caption: {tiktok_caption}")
        
        # Goi uploader y nhu trong bot.py
        rc, stdout, stderr = await run_uploader("tiktok_uploader.py", file_path, tiktok_caption, thumb_path=thumb_path)
        
        if rc == 0:
            print(f"==> TIKTOK UPLOAD THANG CONG: {f}")
        else:
            print(f"==> TIKTOK UPLOAD THAT BAI (Code {rc}): {f}")
            if stderr:
                print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")

if __name__ == "__main__":
    # Fix unicode print on Windows console
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    asyncio.run(test_pipeline())
