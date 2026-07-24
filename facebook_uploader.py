import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

USER_DATA_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster\facebook_profile"

def dismiss_popups(page):
    popup_selectors = [
        "div[role='button']:has-text('Close')",
        "div[aria-label='Close']",
        "div[role='button']:has-text('Not Now')",
        "div[role='button']:has-text('Không phải bây giờ')",
        "div[role='button']:has-text('OK')",
        "div[role='button']:has-text('Got it')",
    ]
    for sel in popup_selectors:
        try:
            btn = page.locator(sel)
            if btn.count() > 0 and btn.first.is_visible(timeout=1000):
                btn.first.click()
                print(f"Da dong popup: {sel}")
                time.sleep(1)
        except:
            pass

def click_next(page):
    # Tim va bam nut Tiep / Next
    next_selectors = [
        "div[role='button']:has-text('Tiếp')",
        "div[role='button']:has-text('Next')",
        "button:has-text('Tiếp')",
        "button:has-text('Next')",
    ]
    for sel in next_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000) and btn.is_enabled():
                btn.click()
                print(f"Da bam nut: {sel}")
                return True
        except:
            continue
    return False

def upload_to_facebook(video_path: str, caption: str, thumb_path: str = None):
    print(f"Dang mo trinh duyet de dang video Facebook Reels: {video_path}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # === BUOC 1: Vao Meta Business Suite va bam Tao Thuoc Phim ===
        print("Truy cap Meta Business Suite...")
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded")
        time.sleep(8)
        dismiss_popups(page)
        
        print("Tim nut Tao thuoc phim / Create reel...")
        try:
            # Uu tien Tao thuoc phim (Reels)
            create_btn_selectors = [
                "a:has-text('Tạo thước phim')",
                "div[role='button']:has-text('Tạo thước phim')",
                "button:has-text('Tạo thước phim')",
                "a:has-text('Create reel')",
                "div[role='button']:has-text('Create reel')",
                "button:has-text('Create reel')",
            ]
            
            clicked_create = False
            for sel in create_btn_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        clicked_create = True
                        print(f"Da bam: {sel}")
                        break
                except:
                    continue
            
            if not clicked_create:
                print("Khong tim thay nut tao thuoc phim. Thu truy cap trang Tao thuoc phim...")
                page.goto("https://business.facebook.com/latest/composer?is_create_reel=true", wait_until="domcontentloaded")
            
            time.sleep(8)
            dismiss_popups(page)
        except Exception as e:
            print(f"Loi khi tim nut tao thuoc phim: {e}")
        
        # === BUOC 2: Them video ===
        print("Tim nut Add video (Thêm video)...")
        time.sleep(3)
        try:
            add_video_selectors = [
                "div[role='button']:has-text('Thêm video')",
                "div[role='button']:has-text('Add video')",
                "div[role='button']:has-text('Tải lên')",
                "div[role='button']:has-text('Upload')",
            ]
            
            uploaded = False
            for sel in add_video_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=2000):
                        # Catch the OS file picker dialog!
                        with page.expect_file_chooser(timeout=10000) as fc_info:
                            btn.click()
                        fc_info.value.set_files(video_path)
                        print(f"Da chon file video qua nut: {sel}")
                        uploaded = True
                        break
                except Exception as e_click:
                    print(f"Thu {sel} that bai: {e_click}")
                    continue
                    
            if not uploaded:
                print("Khong the click nut them video. Thu tim input[type=file] an...")
                file_input = page.locator("input[type='file']")
                if file_input.count() > 0:
                    file_input.first.set_input_files(video_path)
                    print("Da chon file video qua the input!")
                else:
                    raise Exception("Khong the chon file video bang moi cach")
        except Exception as e:
            print(f"Loi khi tai video: {e}")
            browser.close()
            return
        
        # === BUOC 3: Dien caption ===
        print("Cho trang tai xong video de hien thi o nhap text...")
        time.sleep(8)
        dismiss_popups(page)
        
        print(f"Dang dien caption: {caption}")
        try:
            caption_selectors = [
                "div[role='textbox'][aria-label*='Mô tả thước phim']",
                "div[role='textbox'][aria-label*='Describe']",
                "div[role='textbox'][aria-label*='viết']",
                "div[role='textbox'][aria-label*='mô tả']",
                "div[role='textbox']",
                "[contenteditable='true']",
            ]
            
            caption_box = None
            for sel in caption_selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=3000):
                        caption_box = el
                        print(f"Tim thay caption box: {sel}")
                        break
                except:
                    continue
            
            if caption_box:
                caption_box.click()
                time.sleep(0.5)
                page.keyboard.type(caption, delay=30)
                print("Da dien xong caption!")
            else:
                print("Khong tim thay o nhap caption!")
        except Exception as e:
            print(f"Loi dien caption: {e}")
            
        # === BUOC 3.5: Upload thumbnail ===
        if thumb_path and os.path.exists(thumb_path):
            print(f"Dang thu tai len anh bia: {thumb_path}")
            try:
                # Tim nut "Upload image" (Tieng Anh hoac Tieng Viet)
                upload_img_selectors = [
                    "div[role='button']:has-text('Tải hình ảnh lên')",
                    "div[role='button']:has-text('Upload image')",
                    "div:text-is('Tải hình ảnh lên')",
                    "div:text-is('Upload image')",
                ]
                
                clicked_upload = False
                for sel in upload_img_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=2000):
                            with page.expect_file_chooser(timeout=5000) as fc_info:
                                btn.click()
                            fc_info.value.set_files(thumb_path)
                            print(f"Da tai len anh bia qua nut: {sel}")
                            clicked_upload = True
                            time.sleep(3)
                            break
                    except:
                        continue
                if not clicked_upload:
                    print("Khong the tim nut tai anh bia len Facebook")
            except Exception as e:
                print(f"Loi tai anh bia Facebook: {e}")
        
        # === BUOC 4: Cho video tai len ===
        print("Cho video tai len (kiem tra 100%)...")
        max_wait = 300
        waited = 0
        while waited < max_wait:
            time.sleep(5)
            waited += 5
            
            # Kiem tra nut Tiep / Next da active chua
            is_ready = False
            next_selectors = ["div[role='button']:has-text('Tiếp')", "div[role='button']:has-text('Next')"]
            for sel in next_selectors:
                try:
                    btn = page.locator(sel).first
                    # Chi xac nhan ready neu nut dang hien thi va khong bi disabled
                    if btn.is_visible() and btn.is_enabled():
                        is_ready = True
                        break
                except:
                    pass
                    
            if is_ready:
                print(f"  [{waited}s] Da tai xong video (Nut Tiep / Next hien len)")
                break
            else:
                print(f"  [{waited}s] Van dang cho 100%...")
                
        # Bam Next qua cac buoc (Chinh sua -> Chia se)
        print("Tien hanh qua cac buoc (Next)...")
        time.sleep(2)
        click_next(page) # Qua buoc Edit
        time.sleep(3)
        click_next(page) # Qua buoc Share
        time.sleep(3)
        
        # === BUOC 5: Bam nut Chia se / Share ===
        print("Dang bam nut Chia se...")
        try:
            share_selectors = [
                "div[role='button']:has-text('Chia sẻ')",
                "div[role='button']:has-text('Share')",
                "button:has-text('Chia sẻ')",
                "button:has-text('Share')",
            ]
            
            clicked = False
            for sel in share_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=3000) and btn.is_enabled():
                        btn.click()
                        clicked = True
                        print(f"Da bam nut: {sel}")
                        break
                except:
                    continue
            
            if clicked:
                print("Da bam nut Chia se! Cho 15s de he thong ghi nhan...")
                time.sleep(15)
                print("==== HOAN THANH DANG BAI FACEBOOK (THUOC PHIM) ====")
            else:
                print("Khong bam duoc nut Chia se! Sep tu tay bam giup nhe.")
                time.sleep(60)
        except Exception as e:
            print(f"Loi: {e}")
            time.sleep(60)
        
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Su dung: python facebook_uploader.py <video_path> <caption> [<visibility>] [<thumb_path>]")
        sys.exit(1)
    video_file = sys.argv[1]
    caption_text = sys.argv[2]
    thumb_path = sys.argv[4] if len(sys.argv) > 4 else None
    upload_to_facebook(video_file, caption_text, thumb_path)
