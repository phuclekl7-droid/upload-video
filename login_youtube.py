import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster\youtube_profile"

def main():
    print("Dang khoi dong trinh duyet de dang nhap YouTube...")
    print("==================================================")
    print("HUONG DAN:")
    print("1. Trinh duyet se mo trang YouTube Studio.")
    print("2. Dang nhap tai khoan Google/YouTube cua ban.")
    print("3. Khi da vao duoc Trang tong quan cua Studio, TU TAY TAT TRINH DUYET.")
    print("==================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://studio.youtube.com")
        
        print("Trinh duyet da mo. Dang cho ban dang nhap...")
        try:
            page.wait_for_event("close", timeout=0)
        except:
            pass
            
        print("Da dong trinh duyet. Phien dang nhap YouTube da duoc luu!")

if __name__ == "__main__":
    main()
