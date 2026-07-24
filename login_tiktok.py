import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster\tiktok_profile"

def main():
    print("Dang khoi dong trinh duyet de dang nhap Tiktok...")
    print("==================================================")
    print("HUONG DAN:")
    print("1. Cua so trinh duyet se hien len, dung quen dang nhap vao Tiktok (khuyen nghi dung quet ma QR).")
    print("2. Sau khi ban da dang nhap thanh cong va thay trang chu Tiktok...")
    print("3. Hay TU TAY TAT CUA SO TRINH DUYET do di de he thong luu lai phien dang nhap nhe!")
    print("==================================================")
    
    with sync_playwright() as p:
        # Mở Chromium với user_data_dir để lưu lại cookie/session
        # args=["--disable-blink-features=AutomationControlled"] giúp giảm thiểu bị phát hiện là bot
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        if len(browser.pages) > 0:
            page = browser.pages[0]
        else:
            page = browser.new_page()
            
        page.goto("https://www.tiktok.com/login")
        
        # Giữ cho trình duyệt mở cho đến khi người dùng tự tắt
        print("Trinh duyet da mo. Dang cho ban dang nhap...")
        try:
            # Chờ sự kiện trang bị đóng thay vì dùng timeout cố định
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
            
        print("Da dong trinh duyet. Thong tin dang nhap da duoc luu vao thu muc tiktok_profile!")

if __name__ == "__main__":
    main()
