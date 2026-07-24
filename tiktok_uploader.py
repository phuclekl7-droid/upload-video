import sys
import time
import os
from playwright.sync_api import sync_playwright

# Fix loi encoding tren Windows (cp1252 khong hieu tieng Viet)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

USER_DATA_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster\tiktok_profile"

def dismiss_popups(page):
    """Dong tat ca cac popup/dialog phien phuc cua TikTok va Chrome"""
    try:
        # Dong popup "Restore pages?" cua Chrome
        restore_btn = page.locator("button:has-text('Close'), button:has-text('Dismiss'), button[aria-label='Close']")
        if restore_btn.count() > 0:
            for i in range(restore_btn.count()):
                try:
                    if restore_btn.nth(i).is_visible(timeout=1000):
                        restore_btn.nth(i).click()
                except:
                    pass
    except:
        pass
        
    try:
        # Dong popup "Discard this post?" cua TikTok neu hien
        discard_btn = page.locator("button:has-text('Discard')")
        if discard_btn.count() > 0:
            for i in range(discard_btn.count()):
                try:
                    if discard_btn.nth(i).is_visible(timeout=1000):
                        discard_btn.nth(i).click()
                except:
                    pass
    except:
        pass
        
    popup_selectors = [
        "button:has-text('Got it')",
        "button:has-text('OK')",
        "button:has-text('Dismiss')",
        "button:has-text('Skip')",
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

def upload_to_tiktok(video_path: str, caption: str, thumb_path: str = None):
    print(f"Dang mo trinh duyet de dang video: {video_path}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("Truy cap trang TikTok Studio Upload...")
        page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
        time.sleep(8)
        
        # Dong popup neu co
        dismiss_popups(page)
        
        # === BUOC 1: Chon file video ===
        print("Dang tim o tai video len...")
        try:
            file_input = page.locator("input[type='file'][accept='video/*']")
            file_input.wait_for(state="attached", timeout=15000)
            file_input.set_input_files(video_path)
            print("Da chon xong file video!")
        except Exception as e:
            print(f"Cach 1 that bai ({e}), thu cach 2...")
            try:
                with page.expect_file_chooser(timeout=10000) as fc_info:
                    page.locator("button:has-text('Select videos')").click()
                file_chooser = fc_info.value
                file_chooser.set_files(video_path)
                print("Da chon xong file video bang cach 2!")
            except Exception as e2:
                print(f"Ca 2 cach deu that bai: {e2}")
                browser.close()
                return
        
        # === BUOC 2: Cho trang Editor load ra ===
        print("Cho TikTok chuyen sang trang Editor...")
        
        # === BUOC 3: Dien caption ===
        print(f"Dang dien caption: {caption}")
        try:
            caption_selectors = [
                "[contenteditable='true']",
                "div[role='textbox']",
                ".DraftEditor-editorContainer [contenteditable='true']",
                ".public-DraftEditor-content",
                "[data-contents='true']",
            ]
            
            caption_box = None
            for sel in caption_selectors:
                try:
                    el = page.locator(sel).first
                    el.wait_for(state="visible", timeout=15000)
                    if el.is_visible():
                        caption_box = el
                        print(f"Tim thay caption box voi selector: {sel}")
                        break
                except:
                    continue
            
            # Dong popup "Got it" neu hien ra (sau khi load xong editor)
            dismiss_popups(page)
            time.sleep(1)
            
            if caption_box:
                # Click vao o caption
                caption_box.click()
                time.sleep(0.5)
                
                # Xoa sach noi dung cu bang nhieu cach
                try:
                    # Co thu fill("") de xoa, TikTok doi khi support
                    caption_box.fill("")
                except:
                    pass
                time.sleep(0.5)
                caption_box.click() # focus lai lan nua chac an
                page.keyboard.press("Control+A")
                time.sleep(0.5)
                page.keyboard.press("Delete")
                time.sleep(0.5)
                page.keyboard.press("Control+A")
                time.sleep(0.5)
                page.keyboard.press("Backspace")
                time.sleep(0.5)
                # Xoa luon ca mac dinh bang backspace nhieu lan neu can
                for _ in range(5):
                    page.keyboard.press("Backspace")
                time.sleep(0.5)
                
                # Go caption moi
                page.keyboard.type(caption, delay=30)
                print("Da dien xong caption!")
            else:
                print("Khong tim thay o caption!")
                
        except Exception as e:
            print(f"Loi khi dien caption: {e}")
            
        # === BUOC 3.5: Upload thumbnail ===
        if thumb_path and os.path.exists(thumb_path):
            print(f"Dang thu tai len anh bia: {thumb_path}")
            try:
                edit_cover_selectors = [
                    "div:text-is('Edit cover')",
                    "div:text-is('Chỉnh sửa ảnh bìa')",
                    "button:has-text('Edit cover')",
                    "button:has-text('Chỉnh sửa ảnh bìa')"
                ]
                
                for sel in edit_cover_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=2000):
                            btn.click(force=True)
                            time.sleep(2)
                            
                            upload_btn = page.locator("div:text-is('Upload cover'), div:has-text('Upload cover')").last
                            if not upload_btn.is_visible(timeout=2000):
                                upload_btn = page.locator("div:text-is('Tải ảnh bìa lên'), div:has-text('Tải ảnh bìa lên')").last
                                
                            upload_btn.wait_for(state="visible", timeout=10000)
                            with page.expect_file_chooser(timeout=10000) as fc_info:
                                upload_btn.click()
                            fc_info.value.set_files(thumb_path)
                            time.sleep(3)
                            
                            # Bam nut Save/Luu
                            try:
                                save_btn = page.locator("button:has-text('Save'), button:has-text('Lưu')").last
                                save_btn.wait_for(state="visible", timeout=5000)
                                save_btn.click()
                                time.sleep(2)
                            except Exception as e_save:
                                print(f"Khong the bam nut Save anh bia: {e_save}")
                                
                            print(f"Da tai len anh bia qua Tiktok Studio!")
                            time.sleep(3)
                            # Dong dialog cover
                            page.keyboard.press("Escape")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Loi tai anh bia Tiktok: {e}")
        
        # === BUOC 4: Cho video upload xong ===
        print("Cho video upload len server Tiktok (theo doi tien trinh)...")
        max_wait = 300  # Cho toi da 5 phut (video lon can nhieu thoi gian)
        waited = 0
        while waited < max_wait:
            time.sleep(5)
            waited += 5
            
            # Dong popup neu co
            dismiss_popups(page)
            
            # Kiem tra xem con thanh progress khong
            try:
                progress_text = page.locator("text=/\\d+ seconds left/")
                if progress_text.count() > 0 and progress_text.first.is_visible(timeout=1000):
                    txt = progress_text.first.inner_text(timeout=1000)
                    print(f"  [{waited}s] Dang upload: {txt}")
                    continue
            except:
                pass
            
            # Kiem tra nut Post da san sang chua
            try:
                post_btn = page.locator("button:has-text('Post')").last
                if post_btn.is_visible() and post_btn.is_enabled():
                    print(f"  [{waited}s] Nut Post da san sang!")
                    break
            except:
                continue
            
            print(f"  [{waited}s] Van dang cho...")
        
        # === BUOC 5: Bam nut Post ===
        print("Dang tim va bam nut Post...")
        
        # Dong popup lan cuoi truoc khi bam Post
        dismiss_popups(page)
        
        try:
            post_selectors = [
                "button:has-text('Post')",
                "button:has-text('Dang')",
                "button:has-text('Publish')",
            ]
            
            clicked = False
            for sel in post_selectors:
                try:
                    btn = page.locator(sel).last
                    if btn.is_visible() and btn.is_enabled():
                        btn.click()
                        clicked = True
                        print(f"Da bam nut voi selector: {sel}")
                        break
                except:
                    continue
            
            if clicked:
                print("Da bam nut Post! Cho hop thoai xac nhan...")
                time.sleep(3)
                
                # === BUOC 6: Xu ly hop thoai "Continue to post?" ===
                try:
                    post_now_btn = page.locator("button:has-text('Post now')")
                    if post_now_btn.is_visible(timeout=5000):
                        post_now_btn.click()
                        print("Da bam nut 'Post now' trong hop thoai xac nhan!")
                        time.sleep(10)
                        print("==== HOAN THANH DANG BAI ====")
                    else:
                        print("Khong thay hop thoai xac nhan, co the da dang thanh cong!")
                        time.sleep(5)
                        print("==== HOAN THANH DANG BAI ====")
                except:
                    print("Khong thay hop thoai xac nhan, co the da dang thanh cong!")
                    time.sleep(5)
                    print("==== HOAN THANH DANG BAI ====")
            else:
                print("Khong bam duoc nut Post! Sep hay tu tay bam tren trinh duyet.")
                time.sleep(60)
        except Exception as e:
            print(f"Loi khi bam nut Post: {e}")
            time.sleep(60)
        
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Su dung: python tiktok_uploader.py <video_path> <caption> [<visibility>] [<thumb_path>]")
        sys.exit(1)
    video_file = sys.argv[1]
    caption_text = sys.argv[2]
    thumb_path = sys.argv[4] if len(sys.argv) > 4 else None
    upload_to_tiktok(video_file, caption_text, thumb_path)
