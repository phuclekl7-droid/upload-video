import sys
import time
import os
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

USER_DATA_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster\youtube_profile"

def dismiss_popups(page):
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
        # Dismiss any YouTube Studio popups
        close_buttons = page.locator("ytcp-button#close-button, ytcp-button#dismiss-button")
        if close_buttons.count() > 0:
            for i in range(close_buttons.count()):
                try:
                    if close_buttons.nth(i).is_visible(timeout=1000):
                        close_buttons.nth(i).click()
                except:
                    pass
    except:
        pass

def upload_to_youtube(video_path: str, caption: str, visibility: str = "PUBLIC", thumb_path: str = None):
    print(f"Dang mo trinh duyet de dang video len YouTube: {video_path} (Che do: {visibility})")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # === BUOC 1: Vao YouTube Studio ===
        print("Truy cap YouTube Studio...")
        page.goto("https://studio.youtube.com", wait_until="domcontentloaded")
        time.sleep(5)
        dismiss_popups(page)
        
        # === BUOC 2: Bam Tao -> Tai video len ===
        print("Tim nut Tai video len...")
        try:
            try:
                upload_btn = page.locator("#upload-icon").first
                upload_btn.wait_for(state="visible", timeout=10000)
                upload_btn.click()
                time.sleep(2)
            except:
                print("Khong thay nut upload-icon, thu nut Tao...")
                create_btn = page.locator("#create-icon").first
                create_btn.click()
                time.sleep(1)
                upload_item = page.locator("tp-yt-paper-item").first
                upload_item.click()
                time.sleep(2)
        except Exception as e:
            print(f"Loi khi bam nut Tao: {e}. Tiep tuc thu file input...")
        
        # === BUOC 3: Chon file ===
        print("Chon file video...")
        try:
            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(video_path)
            print("Da gui file video!")
        except Exception as e:
            print(f"Loi khi the input file: {e}. Thu bam nut chon file (select-files-button)...")
            try:
                with page.expect_file_chooser(timeout=10000) as fc_info:
                    page.locator("#select-files-button").first.click()
                fc_info.value.set_files(video_path)
                print("Da gui file qua expect_file_chooser!")
            except Exception as e2:
                print(f"Hoan toan that bai khi chon file: {e2}")
                # Take a screenshot to see what's wrong
                page.screenshot(path="youtube_error.png")
                browser.close()
                return
                
        # === BUOC 4: Dien thong tin (Tieu de) ===
        print("Cho hien thi form chi tiet video...")
        time.sleep(8) # Cho upload dialog mo len form dien thong tin
        
        # Youtube gioi han tieu de 100 ky tu, ta nen cat ngan caption neu no qua dai
        if len(caption) > 95:
            caption = caption[:92] + "..."
            
        try:
            # Thuong thi Youtube se tu dien ten file vao form Tieu de.
            # Chung ta phai xoa no di roi moi dien vao
            title_textbox = page.locator("#textbox").first
            title_textbox.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            # Dien text moi
            page.keyboard.type(caption, delay=10)
            print("Da dien tieu de!")
        except Exception as e:
            print(f"Loi dien tieu de: {e}")
            
        # === BUOC 4.5: Upload thumbnail ===
        if thumb_path and os.path.exists(thumb_path):
            print(f"Dang tai len anh bia: {thumb_path}")
            try:
                # Dong moi popup truoc khi thao tac
                dismiss_popups(page)
                
                # Cuon len phan Hinh thu nho de dam bao nut "Tai tep len" hien thi
                try:
                    thumb_section = page.locator("text=Hình thu nhỏ").first
                    thumb_section.scroll_into_view_if_needed()
                    time.sleep(1)
                except:
                    # Neu khong tim thay text, cuon len dau trang
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(1)
                
                # Click nut "Tai tep len" trong phan Hinh thu nho roi dung file chooser
                upload_btn = page.locator("text=Tải tệp lên").first
                upload_btn.wait_for(state="visible", timeout=10000)
                with page.expect_file_chooser(timeout=10000) as fc_info:
                    upload_btn.click()
                fc_info.value.set_files(thumb_path)
                time.sleep(5)
                print("Da tai len anh bia thanh cong!")
            except Exception as e:
                print(f"Khong the tai anh bia: {e}")
                try:
                    page.screenshot(path="youtube_thumb_error.png")
                except:
                    pass

        # === BUOC 5: Chon Khong danh cho tre em ===
        print("Chon doi tuong nguoi xem...")
        try:
            kids_radio = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
            kids_radio.click()
        except Exception as e:
            print(f"Khong the chon Khong danh cho tre em: {e}")
            
        # === BUOC 6: Bam NEXT cho den buoc cuoi ===
        print("Tien hanh qua cac buoc...")
        # Thong thuong co 3-4 buoc: Chi tiet -> Kiem tra -> Chinh sua -> Hien thi
        for i in range(3):
            time.sleep(2)
            try:
                next_btn = page.locator("#next-button").first
                if next_btn.is_visible() and next_btn.is_enabled():
                    next_btn.click()
                    print(f"Da bam Next lan {i+1}")
            except:
                pass
                
        # === BUOC 7: Chon Hien thi (Cong khai / Khong cong khai) ===
        print(f"Chon che do {visibility}...")
        time.sleep(2)
        try:
            public_radio = page.locator(f"tp-yt-paper-radio-button[name='{visibility}']").first
            public_radio.click()
        except Exception as e:
            print(f"Loi chon hien thi: {e}")
            
        # === BUOC 8: Cho upload xong & Bam Xuat ban ===
        print("Cho video upload len server YouTube...")
        max_wait = 300
        waited = 0
        while waited < max_wait:
            time.sleep(5)
            waited += 5
            
            try:
                # Kiem tra xem co bao loi hay dang upload
                # Neu upload xong thi nut Done / Xuat ban se ready
                done_btn = page.locator("#done-button").first
                if done_btn.is_visible() and done_btn.is_enabled():
                    print(f"  [{waited}s] Nut Xuat ban da san sang!")
                    break
            except:
                pass
            print(f"  [{waited}s] Van dang cho 100%...")
            
        print("Dang bam nut Xuat ban (Publish)...")
        try:
            done_btn = page.locator("#done-button").first
            done_btn.click()
            print("Da bam Xuat ban! Dang theo doi tien do tai len cua YouTube...")
            
            waited_after = 0
            while waited_after < 3600:  # Cho toi da 1 tieng cho cac video cuc nang
                time.sleep(5)
                waited_after += 5
                try:
                    # Kiem tra xem modal chia se video (Xuat ban thanh cong) co hien len khong
                    if page.locator("ytcp-video-share-dialog").is_visible():
                        print("Da thay thong bao Xuat ban thanh cong!")
                        break
                    
                    # Hoac kiem tra text canh bao "Vui long luon mo the"
                    page_text = page.locator("body").inner_text().lower()
                    if "vui lòng luôn mở thẻ" not in page_text and "keep this browser tab open" not in page_text and "đang tải video của bạn lên" not in page_text and "uploading your video" not in page_text:
                        print(f"[{waited_after}s] Khong con yeu cau giu nguyen tab. Upload file da hoan tat 100%! Da an toan de thoat!")
                        break
                except:
                    pass
                print(f"  [{waited_after}s] Van dang doi YouTube tai file len may chu... (Neu video nang co the mat vai phut)")
                
            time.sleep(5)
            print("==== HOAN THANH DANG BAI YOUTUBE ====")
        except Exception as e:
            print(f"Loi bam nut Xuat ban: {e}")
            time.sleep(10)
            
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Su dung: python youtube_uploader.py <video_path> <caption> [<visibility>] [<thumb_path>]")
        sys.exit(1)
    video_file = sys.argv[1]
    caption_text = sys.argv[2]
    visibility_arg = sys.argv[3] if len(sys.argv) > 3 else "PUBLIC"
    thumb_arg = sys.argv[4] if len(sys.argv) > 4 else None
    upload_to_youtube(video_file, caption_text, visibility_arg, thumb_arg)
