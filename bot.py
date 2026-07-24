import os
import sys
import asyncio
import logging
import datetime
import random
import threading
import http.server
import socketserver
import subprocess
import json
import uuid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, InlineQueryHandler
import video_tools
import re
import glob
from PIL import Image

TOKEN = "8575193471:AAFB4ahDWmPt3VDwuTCEEhpQPXsefNNDuH4"
BOT_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster"
VIDEO_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster\AutoPost"

# Variables
DEFAULT_HASHTAGS = "#fyp #xuhuong #trending"
stop_posting_flags = {}
callback_map = {}
import hashlib

def get_callback_id(text):
    h = hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    callback_map[h] = text
    return h

waiting_for_platform = {}
waiting_for_schedule_time = {}
waiting_for_caption = {}

# Keep track of admin
admin_chat_id = None
application_instance = None

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

VIDEO_DIR = r"C:\Users\COMPUTER\AppData\Local\CapCut\Videos\AutoPost"
os.makedirs(VIDEO_DIR, exist_ok=True)

DEFAULT_HASHTAGS = "#nguyetquanhienvietsub #fyp"
BOT_DIR = r"C:\Users\COMPUTER\.gemini\antigravity\scratch\telegram_auto_poster"

PUBLIC_URL = ""

def start_web_server():
    os.chdir(BOT_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        httpd.serve_forever()

def start_localtunnel():
    global PUBLIC_URL
    process = subprocess.Popen(
        ['npx.cmd', '-y', 'localtunnel', '--port', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=BOT_DIR
    )
    for line in iter(process.stdout.readline, ''):
        if "your url is:" in line:
            PUBLIC_URL = line.split("is:")[1].strip()
            print("Web App URL:", PUBLIC_URL)
            break

# Khởi chạy server và tunnel ngầm
threading.Thread(target=start_web_server, daemon=True).start()
threading.Thread(target=start_localtunnel, daemon=True).start()

# Trang thai: user dang cho nhap ten (value = file_path)
waiting_for_caption = {}
# Trang thai: user da nhap ten xong, cho chon nen tang (value = {file_path, caption})
waiting_for_platform = {}
# Trang thai: flag de dung dang video hang loat
stop_posting_flags = {}
callback_map = {}
import hashlib

def get_callback_id(text):
    h = hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    callback_map[h] = text
    return h

# Trang thai: user dang cho nhap thoi gian hen gio (value = {type, target_platform})
waiting_for_schedule_time = {}

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Xem video", callback_data="cmd_list"),
         InlineKeyboardButton("📖 Hướng dẫn", callback_data="cmd_help")],
        [InlineKeyboardButton("🟢 Trạng thái", callback_data="cmd_status")]
    ])

def platform_keyboard(file_path, caption):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 TikTok", callback_data="platform|tiktok"),
         InlineKeyboardButton("📘 Facebook", callback_data="platform|facebook")],
        [InlineKeyboardButton("🔴 YouTube", callback_data="yt_vis|platform|youtube")],
        [InlineKeyboardButton("🚀 Tất cả nền tảng", callback_data="yt_vis|platform|all")],
        [InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]
    ])

def back_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Xem video", callback_data="cmd_list"),
         InlineKeyboardButton("🏠 Về đầu", callback_data="cmd_start")]
    ])

def build_caption(user_text: str) -> str:
    if user_text.strip():
        return f"{user_text.strip()} {DEFAULT_HASHTAGS}"
    return DEFAULT_HASHTAGS

async def run_uploader(script_name: str, video_path: str, caption: str, visibility: str = "", thumb_path: str = ""):
    args = [sys.executable, script_name, video_path, caption]
    if visibility:
        args.append(visibility)
    elif thumb_path: # If we need to pass thumb_path but no visibility (like FB/TikTok), pass an empty string for visibility to maintain position
        args.append("PUBLIC") 
        
    if thumb_path:
        args.append(thumb_path)
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=BOT_DIR
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"[{script_name}] THAT BAI (Code {process.returncode})", flush=True)
        if stderr:
            print(f"[{script_name}] STDERR:\n{stderr.decode('utf-8', errors='replace')}", flush=True)
        if stdout:
            print(f"[{script_name}] STDOUT:\n{stdout.decode('utf-8', errors='replace')}", flush=True)
    else:
        print(f"[{script_name}] THANH CONG!", flush=True)
        if stdout:
             print(f"[{script_name}] STDOUT:\n{stdout.decode('utf-8', errors='replace')}", flush=True)
             
    return process.returncode, stdout, stderr

async def post_all_task(chat_id, context, files, target_platform="all", is_split=False, split_parts=5, base_name=None, custom_caption=None):
    stop_posting_flags[chat_id] = False
    
    thumb_tiktok = None
    thumb_fb_yt = None
    
    if base_name:
        potential_thumbs = []
        for ext in ['.jpg', '.jpeg', '.png']:
            potential_thumbs.extend(glob.glob(os.path.join(VIDEO_DIR, f"{base_name}*{ext}")))
            
        for p in potential_thumbs:
            try:
                with Image.open(p) as img:
                    w, h = img.size
                    ratio = w / h
                    # 3:4 is 0.75, 16:9 is 1.777
                    if 0.7 <= ratio <= 0.8:
                        thumb_tiktok = p
                    elif 1.6 <= ratio <= 1.9:
                        thumb_fb_yt = p
            except Exception as e:
                print(f"Khong the doc anh {p}: {e}")
                
        # Neu co anh nhung khong khop dung ti le tren, cu lay tam anh dau tien
        if potential_thumbs:
            if not thumb_tiktok:
                thumb_tiktok = potential_thumbs[0]
            if not thumb_fb_yt:
                thumb_fb_yt = potential_thumbs[0]
                
    for original_f in files:
        if stop_posting_flags.get(chat_id):
            await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
            return
            
        original_file_path = os.path.join(VIDEO_DIR, original_f)
        
        # 0. Xu ly caption
        base_cap = custom_caption if custom_caption else os.path.splitext(original_f)[0]
        
        # 1. DANG YOUTUBE (Truoc khi cat, dung ban full)
        result_yt = "⏭️ YouTube: Bỏ qua"
        if "youtube" in target_platform or "all" in target_platform:
            yt_vis = "UNLISTED" if "unlisted" in target_platform else "PUBLIC"
            thumb_msg = "\n🖼️ Dùng ảnh bìa nhóm" if thumb_fb_yt else ""
            await context.bot.send_message(chat_id, f"🔴 Tớ đang tải bản FULL của {original_f} lên YouTube...\n📝 Caption: {base_cap}{thumb_msg}")
            
            if thumb_fb_yt:
                rc3, stdout3, stderr3 = await run_uploader("youtube_uploader.py", original_file_path, base_cap, yt_vis, thumb_path=thumb_fb_yt)
            else:
                rc3, stdout3, stderr3 = await run_uploader("youtube_uploader.py", original_file_path, base_cap, yt_vis)
            result_yt = f"✅ YouTube ({yt_vis}): Thành công!" if rc3 == 0 else f"❌ YouTube ({yt_vis}): Thất bại"
            await context.bot.send_message(chat_id, f"📊 Kết quả YouTube '{original_f}':\n{result_yt}")
            
            if stop_posting_flags.get(chat_id):
                await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
                return
        
        if is_split:
            await context.bot.send_message(chat_id, f"🔪 Tớ đang cặm cụi cắt video {original_f} thành {split_parts} phần...")
            loop = asyncio.get_running_loop()
            split_files = await loop.run_in_executor(None, video_tools.split_video, original_file_path, split_parts)
        else:
            split_files = [original_file_path]
            
        for file_path in split_files:
            if stop_posting_flags.get(chat_id):
                await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
                return
                
            f = os.path.basename(file_path)
            raw_caption = base_cap if not is_split else os.path.splitext(f)[0]
            tiktok_caption = build_caption(raw_caption)
            fb_caption = raw_caption
            
            thumb_msg = ""
            if thumb_tiktok or thumb_fb_yt:
                thumb_msg = "\n🖼️ Dùng ảnh bìa nhóm"
            await context.bot.send_message(chat_id, f"🚀 Tớ đang bắt đầu đăng: {f}\n📝 Caption: {fb_caption}{thumb_msg}")
        
            # Chay TikTok
            if "tiktok" in target_platform or "all" in target_platform:
                if thumb_tiktok:
                    rc1, stdout1, stderr1 = await run_uploader("tiktok_uploader.py", file_path, tiktok_caption, thumb_path=thumb_tiktok)
                else:
                    rc1, stdout1, stderr1 = await run_uploader("tiktok_uploader.py", file_path, tiktok_caption)
                result_tt = "✅ TikTok: Thành công!" if rc1 == 0 else "❌ TikTok: Thất bại"
            else:
                result_tt = "⏭️ TikTok: Bỏ qua"
            
            if stop_posting_flags.get(chat_id):
                await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
                return
                
            # Chay Facebook
            if "facebook" in target_platform or "all" in target_platform:
                if thumb_fb_yt:
                    rc2, stdout2, stderr2 = await run_uploader("facebook_uploader.py", file_path, fb_caption, thumb_path=thumb_fb_yt)
                else:
                    rc2, stdout2, stderr2 = await run_uploader("facebook_uploader.py", file_path, fb_caption)
                result_fb = "✅ Facebook: Thành công!" if rc2 == 0 else "❌ Facebook: Thất bại"
            else:
                result_fb = "⏭️ Facebook: Bỏ qua"
            
            if stop_posting_flags.get(chat_id):
                await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
                return
                
        await context.bot.send_message(chat_id, f"📊 Kết quả phần '{f}':\n\n{result_tt}\n{result_fb}")
        
        if is_split and file_path != original_file_path:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Không thể xóa file {file_path}: {e}")
                
        if original_f != files[-1] or file_path != split_files[-1]:
            delay = random.randint(15, 30)
            await context.bot.send_message(chat_id, f"⏳ Nghỉ {delay} giây trước khi đăng video tiếp theo để tránh bị chặn...")
            for _ in range(delay):
                if stop_posting_flags.get(chat_id):
                    await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
                    return
                await asyncio.sleep(1)
        
    await context.bot.send_message(chat_id, "🎉 Fufu, tớ đã đăng xong toàn bộ video cho cậu rồi đấy! Cậu vất vả rồi!", reply_markup=main_menu_keyboard())
    stop_posting_flags.pop(chat_id, None)

async def execute_scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    data = job.data
    chat_id = data["chat_id"]
    
    if data["type"] == "post_all":
        try:
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await context.bot.send_message(chat_id, f"Đến giờ hẹn rồi mà thư mục lại trống trơn... Cậu quên bỏ video vào đúng không...\n{VIDEO_DIR}")
                return
            
            await context.bot.send_message(
                chat_id, 
                f"⏰ ĐẾN GIỜ HẸN! Tớ bắt đầu đăng toàn bộ {len(files)} video nhé!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Dừng đăng tự động", callback_data="stop_post_all")]])
            )
            is_split = data.get("is_split", False)
            split_parts = data.get("split_parts", 5)
            asyncio.create_task(post_all_task(chat_id, context, files, data["target_platform"], is_split, split_parts))
        except Exception as e:
            await context.bot.send_message(chat_id, f"Ưm... Có lỗi hẹn giờ mất rồi: {e}")

async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jobs = context.job_queue.jobs()
    if not jobs:
        await update.message.reply_text("Hiện tại không có lịch hẹn nào đang chờ cả, cậu à.", reply_markup=main_menu_keyboard())
        return
    
    msg = "📋 CÁC LỊCH ĐANG HẸN:\n\n"
    for idx, job in enumerate(jobs, 1):
        local_time = job.next_t.astimezone().strftime('%H:%M %d/%m/%Y')
        msg += f"{idx}. Lúc {local_time} - Đăng toàn bộ\n"
        
    await update.message.reply_text(msg, reply_markup=main_menu_keyboard())

async def set_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Khởi động bot"),
        BotCommand("list", "Xem video trong máy"),
        BotCommand("jobs", "Xem danh sách hẹn giờ"),
        BotCommand("webapp", "Mở Ứng dụng Giao diện"),
        BotCommand("help", "Hướng dẫn sử dụng"),
        BotCommand("status", "Kiểm tra trạng thái")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global admin_chat_id
    admin_chat_id = update.message.chat_id
    await update.message.reply_html(
        f"Chào cậu... Tớ đã sẵn sàng rồi.\n"
        f"Thư mục video:\n<code>{VIDEO_DIR}</code>\n\n"
        "Cậu muốn tớ giúp gì nào? Tớ có thể đăng lên cả TikTok và Facebook đấy.",
        reply_markup=main_menu_keyboard()
    )

def group_videos(files):
    groups = {}
    r = re.compile(r'^(.*?)(?:\s*(?:Tập|Part|Ep|Phần)?\s*\d+(?:-\d+)?)?(?:\.mp4|\.mov|\.avi)$', re.IGNORECASE)
    for f in files:
        m = r.match(f)
        if m:
            base_name = m.group(1).strip()
            if base_name not in groups:
                groups[base_name] = []
            groups[base_name].append(f)
    
    # Sort files naturally inside each group
    for base_name in groups:
        groups[base_name].sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
        
    return groups

async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        if not files:
            await update.message.reply_text(
                f"Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé. Cậu xuất video từ CapCut vào đây đi:\n{VIDEO_DIR}",
                reply_markup=main_menu_keyboard()
            )
            return
        groups = group_videos(files)
        
        msg = "Tớ tìm thấy rồi. Video đang chờ đăng:\n\n"
        for i, (base_name, group_files) in enumerate(groups.items(), 1):
            thumb = ""
            for ext in ['.jpg', '.png']:
                if os.path.exists(os.path.join(VIDEO_DIR, f"{base_name}{ext}")):
                    thumb = " 🖼️"
                    break
            msg += f"{i}. Nhóm <code>{base_name}</code> ({len(group_files)} tập){thumb}\n"
        msg += f"\nHashtag mặc định: {DEFAULT_HASHTAGS}\nBấm 'Chọn nhóm' để đặt lệnh đăng."
        
        buttons = []
        for base_name in groups:
            short_name = base_name[:25] + "..." if len(base_name) > 25 else base_name
            cb_id = get_callback_id(base_name)
            buttons.append([InlineKeyboardButton(f"✅ Chọn nhóm '{short_name}'", callback_data=f"edit_name|{cb_id}")])
        buttons.append([InlineKeyboardButton("🚀 Đăng TOÀN BỘ tất cả", callback_data="post_all_menu")])
        buttons.append([InlineKeyboardButton("📖 Hướng dẫn", callback_data="cmd_help")])
        await update.message.reply_html(msg, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}", reply_markup=main_menu_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 CÁCH ĐĂNG VIDEO:\n\n"
        "1. Gõ /list để xem danh sách video\n"
        "2. Bấm 'Sửa tên' của video muốn đăng\n"
        "3. Gõ tên/caption (ví dụ: 1 2 3)\n"
        "4. Chọn nền tảng: 🎵 TikTok, 📘 Facebook, hoặc 🚀 Cả hai\n"
        "5. Tớ tự động đăng!\n\n"
        f"Hashtag mặc định: {DEFAULT_HASHTAGS}"
    )
    await update.message.reply_text(help_text, reply_markup=back_menu_keyboard())

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🟢 Hệ thống vẫn ổn định. Tớ luôn sẵn sàng đăng TikTok và Facebook cho cậu.", reply_markup=main_menu_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "cmd_list":
        try:
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await query.edit_message_text(f"Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé.\n{VIDEO_DIR}", reply_markup=main_menu_keyboard())
                return
            groups = group_videos(files)
            
            msg = "Tớ tìm thấy rồi. Video đang chờ đăng:\n\n"
            for i, (base_name, group_files) in enumerate(groups.items(), 1):
                thumb = ""
                for ext in ['.jpg', '.png']:
                    if os.path.exists(os.path.join(VIDEO_DIR, f"{base_name}{ext}")):
                        thumb = " 🖼️"
                        break
                msg += f"{i}. Nhóm <code>{base_name}</code> ({len(group_files)} tập){thumb}\n"
            msg += f"\nHashtag mặc định: {DEFAULT_HASHTAGS}\nBấm 'Chọn nhóm' để đặt lệnh đăng."
            
            buttons = []
            for base_name in groups:
                short_name = base_name[:25] + "..." if len(base_name) > 25 else base_name
                cb_id = get_callback_id(base_name)
                buttons.append([InlineKeyboardButton(f"✅ Chọn nhóm '{short_name}'", callback_data=f"edit_name|{cb_id}")])
            buttons.append([InlineKeyboardButton("🚀 Đăng TOÀN BỘ tất cả", callback_data="post_all_menu")])
            buttons.append([InlineKeyboardButton("📖 Hướng dẫn", callback_data="cmd_help")])
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
        except Exception as e:
            await query.edit_message_text(f"Lỗi: {e}", reply_markup=main_menu_keyboard())
    
    elif data == "cmd_help":
        await query.edit_message_text(
            "📖 CÁCH ĐĂNG:\n1. /list → 2. Sửa tên → 3. Gõ caption → 4. Chọn nền tảng\n"
            "Hoặc bấm nút 'Đăng TOÀN BỘ' để tớ tự lấy tên file làm caption và đăng hết!\n\n"
            f"Hashtag mặc định: {DEFAULT_HASHTAGS}",
            reply_markup=back_menu_keyboard()
        )
    
    elif data == "cmd_status":
        await query.edit_message_text("🟢 Mọi thứ vẫn ổn cả.", reply_markup=main_menu_keyboard())
    
    elif data == "cmd_start":
        await query.edit_message_text(f"Tớ đã chuẩn bị sẵn sàng rồi đây.\nThư mục hiện tại: {VIDEO_DIR}", reply_markup=main_menu_keyboard())
    
    elif data.startswith("edit_name|"):
        cb_id = data.split("|", 1)[1]
        base_name = callback_map.get(cb_id, cb_id) # fallback to cb_id if it was a real name before restart
        
        files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        groups = group_videos(files)
        count = len(groups.get(base_name, []))
        
        waiting_for_caption[user_id] = base_name
        short_name = base_name[:30] + "..." if len(base_name) > 30 else base_name
        await query.edit_message_text(
            f"✏️ Nhóm Video: {short_name} ({count} tập)\n\n"
            f"Gõ tên/caption cho nhóm này đi cậu.\n"
            f"(TikTok sẽ tự thêm {DEFAULT_HASHTAGS}, Facebook thì không)\n\n"
            f"💡 Ví dụ: gõ 'Phim hay' hoặc 'Hôm nay trời đẹp'",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]])
        )
    
    elif data == "cancel_edit":
        waiting_for_caption.pop(user_id, None)
        waiting_for_platform.pop(user_id, None)
        waiting_for_schedule_time.pop(user_id, None)
        await query.edit_message_text("Tớ đã hủy lệnh rồi. Cậu muốn tớ làm gì tiếp theo nào?", reply_markup=main_menu_keyboard())
    
    elif data == "post_all_menu":
        try:
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await query.edit_message_text(f"Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé.\n{VIDEO_DIR}", reply_markup=main_menu_keyboard())
                return
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 Chỉ TikTok", callback_data="post_all|tiktok"),
                 InlineKeyboardButton("📘 Chỉ Facebook", callback_data="post_all|facebook")],
                [InlineKeyboardButton("🔴 Chỉ YouTube", callback_data="yt_vis|post_all|youtube")],
                [InlineKeyboardButton("🚀 Tất cả nền tảng", callback_data="yt_vis|post_all|all")],
                [InlineKeyboardButton("⏳ Hẹn giờ đăng toàn bộ", callback_data="yt_vis|schedule|all")],
                [InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]
            ])
            await query.edit_message_text(f"Cậu muốn tớ đăng toàn bộ {len(files)} video lên đâu?", reply_markup=keyboard)
        except Exception as e:
            await query.message.reply_text(f"Lỗi: {e}")
            
    elif data.startswith("yt_vis|"):
        parts = data.split("|")
        action = parts[1]
        target = parts[2]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👁️ Công khai", callback_data=f"{action}|{target}_public")],
            [InlineKeyboardButton("🔒 Không công khai", callback_data=f"{action}|{target}_unlisted")],
            [InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]
        ])
        
        if action == "schedule":
            text = "Cậu muốn hẹn giờ đăng YouTube ở chế độ nào?"
        else:
            text = "Cậu muốn đăng YouTube ở chế độ nào?"
            
        await query.edit_message_text(text, reply_markup=keyboard)
            
    elif data.startswith("schedule|"):
        target_platform = data.split("|")[1]
        waiting_for_schedule_time[user_id] = {"type": "post_all", "target_platform": target_platform}
        await query.edit_message_text(
            "⏳ Cậu muốn hẹn giờ đăng toàn bộ video (TikTok + FB + YT)?\n\n"
            "Hãy gõ thời gian muốn đăng theo định dạng:\n"
            "👉 HH:MM (ví dụ: 15:30 - đăng hôm nay)\n"
            "👉 HH:MM DD/MM (ví dụ: 15:30 25/10)\n\n"
            "(Lưu ý: Máy tính của cậu phải ĐANG BẬT vào lúc đó nhé)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]])
        )
            
    elif data.startswith("post_all|"):
        target_platform = data.split("|")[1]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Không cắt (Giữ nguyên)", callback_data=f"start_all|{target_platform}|0")],
            [InlineKeyboardButton("🔪 Cắt 2 phần", callback_data=f"start_all|{target_platform}|2"),
             InlineKeyboardButton("🔪 Cắt 3 phần", callback_data=f"start_all|{target_platform}|3")],
            [InlineKeyboardButton("🔪 Cắt 4 phần", callback_data=f"start_all|{target_platform}|4"),
             InlineKeyboardButton("🔪 Cắt 5 phần", callback_data=f"start_all|{target_platform}|5")],
            [InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]
        ])
        await query.edit_message_text(f"Cậu có muốn tớ CẮT các video này thành nhiều phần trước khi đăng không?", reply_markup=keyboard)
        
    elif data.startswith("start_all|"):
        target_platform = data.split("|")[1]
        split_parts = int(data.split("|")[2])
        is_split = split_parts > 0
        try:
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await query.edit_message_text(f"Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé.\n{VIDEO_DIR}", reply_markup=main_menu_keyboard())
                return
            
            platform_name_map = {
                "tiktok": "Chỉ TikTok",
                "facebook": "Chỉ Facebook",
                "youtube_public": "Chỉ YouTube (Công khai)",
                "youtube_unlisted": "Chỉ YouTube (Không công khai)",
                "all_public": "Tất cả nền tảng (YT Công khai)",
                "all_unlisted": "Tất cả nền tảng (YT Không công khai)"
            }
            
            await query.edit_message_text(
                f"🚀 Tớ bắt đầu đăng toàn bộ {len(files)} video lên {platform_name_map.get(target_platform, '...')} nhé! Cậu cứ để tớ lo.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Dừng đăng tự động", callback_data="stop_post_all")]])
            )
            # Chay background
            asyncio.create_task(post_all_task(query.message.chat_id, context, files, target_platform, is_split=is_split, split_parts=split_parts))
        except Exception as e:
            await query.message.reply_text(f"Lỗi: {e}")
            
    elif data == "stop_post_all":
        stop_posting_flags[query.message.chat_id] = True
        await query.edit_message_text("🛑 Tớ nhận lệnh rồi... Tớ sẽ dừng lại ngay sau khi đăng xong video hiện tại nhé.", reply_markup=main_menu_keyboard())
    
    elif data.startswith("platform|"):
        platform = data.split("|", 1)[1]
        
        if user_id not in waiting_for_platform:
            await query.edit_message_text("Ưm... Hết thời gian chờ mất rồi. Cậu thao tác lại từ /list giúp tớ nhé.", reply_markup=main_menu_keyboard())
            return
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Không cắt (Giữ nguyên)", callback_data=f"start_group|{platform}|0")],
            [InlineKeyboardButton("🔪 Cắt 2 phần", callback_data=f"start_group|{platform}|2"),
             InlineKeyboardButton("🔪 Cắt 3 phần", callback_data=f"start_group|{platform}|3")],
            [InlineKeyboardButton("🔪 Cắt 4 phần", callback_data=f"start_group|{platform}|4"),
             InlineKeyboardButton("🔪 Cắt 5 phần", callback_data=f"start_group|{platform}|5")],
            [InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]
        ])
        await query.edit_message_text(f"Cậu có muốn tớ CẮT nhóm video này ra thành nhiều phần nhỏ không?", reply_markup=keyboard)

    elif data.startswith("start_group|"):
        parts = data.split("|")
        platform = parts[1]
        split_parts = int(parts[2])
        is_split = split_parts > 0
        
        if user_id not in waiting_for_platform:
            await query.edit_message_text("Ưm... Hết thời gian chờ mất rồi. Cậu thao tác lại từ /list giúp tớ nhé.", reply_markup=main_menu_keyboard())
            return
            
        info = waiting_for_platform.pop(user_id)
        base_name = info["file_path"]
        raw_caption = info["caption"]
        
        files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        groups = group_videos(files)
        target_files = groups.get(base_name, [base_name])
        
        if platform == "tiktok":
            await query.edit_message_text(f"🎵 Tớ đang cặm cụi đăng nhóm {base_name} lên TikTok...")
        elif platform == "facebook":
            await query.edit_message_text(f"📘 Tớ đang tải nhóm {base_name} lên Facebook Reels...")
        elif platform.startswith("youtube"):
            yt_vis = "UNLISTED" if "unlisted" in platform else "PUBLIC"
            await query.edit_message_text(f"🔴 Tớ đang tải nhóm {base_name} lên YouTube ({yt_vis})...")
            platform = "youtube_unlisted" if "unlisted" in platform else "youtube_public"
        elif platform.startswith("all"):
            yt_vis = "UNLISTED" if "unlisted" in platform else "PUBLIC"
            await query.edit_message_text(f"🚀 Tớ đang tải nhóm {base_name} lên CẢ BA nền tảng (YouTube: {yt_vis})...")
            platform = "all_unlisted" if "unlisted" in platform else "all_public"
            
        asyncio.create_task(post_all_task(query.message.chat_id, context, target_files, platform, is_split=is_split, split_parts=split_parts, base_name=base_name, custom_caption=raw_caption))

async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != "private":
        await update.message.reply_text("❌ Chức năng WebApp xịn xò này chỉ dùng được khi cậu nhắn tin RIÊNG với tớ thôi! Cậu vào hòm thư riêng nhắn cho tớ nhé.")
        return
        
    if not PUBLIC_URL:
        await update.message.reply_text("⏳ Máy chủ WebApp đang rục rịch khởi động, cậu đợi tớ vài giây rồi thử lại nha...")
        return
        
    try:
        files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        count = len(files)
    except:
        count = 0
        
    url = f"{PUBLIC_URL}/webapp.html?count={count}"
    
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Mở Giao Diện WebApp", web_app=WebAppInfo(url=url))]],
        resize_keyboard=True
    )
    await update.message.reply_text("Cậu bấm vào nút bên dưới để mở giao diện WebApp tớ vừa chuẩn bị nhé!", reply_markup=reply_markup)

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data_str = update.message.web_app_data.data
    try:
        data = json.loads(data_str)
        chat_id = update.message.chat_id
        target_platform = data.get("platform")
        is_schedule = data.get("schedule")
        is_split = data.get("split", False)
        split_parts = data.get("splitParts", 5)
        
        platform_names = {
            "tiktok": "TikTok",
            "facebook": "Facebook",
            "youtube_public": "YouTube (Công khai)",
            "youtube_unlisted": "YouTube (Không công khai)",
            "all_public": "Tất cả (YT Công khai)",
            "all_unlisted": "Tất cả (YT Không công khai)"
        }
        name_str = platform_names.get(target_platform, target_platform)
        
        if is_schedule:
            time_str = data.get("time", "").strip()
            now = datetime.datetime.now()
            if " " in time_str:
                time_part, date_part = time_str.split(" ")
                h, m = map(int, time_part.split(":"))
                day, month = map(int, date_part.split("/"))
                target_time = now.replace(month=month, day=day, hour=h, minute=m, second=0, microsecond=0)
                if target_time < now:
                    target_time = target_time.replace(year=now.year + 1)
            else:
                h, m = map(int, time_str.split(":"))
                target_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if target_time < now:
                    target_time = target_time + datetime.timedelta(days=1)
                    
            delay = (target_time - now).total_seconds()
            if delay <= 0:
                await update.message.reply_text("❌ Thời gian cậu hẹn đã trôi qua mất rồi!", reply_markup=ReplyKeyboardRemove())
                return
                
            job_data = {
                "chat_id": chat_id,
                "type": "post_all",
                "target_platform": target_platform,
                "is_split": is_split,
                "split_parts": split_parts
            }
            context.job_queue.run_once(execute_scheduled_job, delay, data=job_data, name=f"Job_WebApp_{chat_id}_{int(now.timestamp())}")
            
            await update.message.reply_text(f"✅ Lịch hẹn WebApp: Đăng lên {name_str} lúc {target_time.strftime('%H:%M %d/%m/%Y')}", reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text("Cậu có thể gõ /jobs để xem lại lịch nha.", reply_markup=main_menu_keyboard())
        else:
            await update.message.reply_text(f"🚀 Nhận lệnh WebApp: Bắt đầu đăng lên {name_str} ngay lập tức!", reply_markup=ReplyKeyboardRemove())
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            groups = group_videos(files)
            target_files = groups.get(filename, [filename]) if filename in groups else [filename]
            asyncio.create_task(post_all_task(chat_id, context, target_files, target_platform, is_split, split_parts, base_name=filename))
            
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi WebApp: {e}")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    
    try:
        files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        groups = group_videos(files)
    except:
        groups = {}
        
    if query:
        groups = {k: v for k, v in groups.items() if query.lower() in k.lower()}
        
    results = []
    
    if not groups:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Không tìm thấy video nào!",
                description="Thư mục đang trống hoặc tìm kiếm không khớp.",
                input_message_content=InputTextMessageContent(
                    "Hiện tại tao đang không có cái video nào chờ đăng cả! Chắc phải đợi sếp làm thêm video thôi."
                )
            )
        )
    else:
        for base_name, group_files in list(groups.items())[:50]:
            count = len(group_files)
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"🎬 Nhóm: {base_name} ({count} tập)",
                    description="Gửi tin nhắn khoe nhóm video này!",
                    input_message_content=InputTextMessageContent(
                        f"Ê tụi bây! Tao đang có {count} tập video siêu đỉnh mang tên:\n"
                        f"👉 *{base_name}*\n"
                        f"Chuẩn bị đăng lên mạng rồi, lót dép hóng đi nhé! 😎",
                        parse_mode="Markdown"
                    )
                )
            )
            
    await update.inline_query.answer(results, cache_time=5)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global admin_chat_id
    admin_chat_id = update.message.chat_id
    
    text = update.message.text or ""
    user_id = update.effective_user.id
    
    # User dang cho nhap thoi gian hen gio
    if user_id in waiting_for_schedule_time:
        time_str = text.strip()
        try:
            now = datetime.datetime.now()
            if " " in time_str:
                time_part, date_part = time_str.split(" ")
                h, m = map(int, time_part.split(":"))
                day, month = map(int, date_part.split("/"))
                target_time = now.replace(month=month, day=day, hour=h, minute=m, second=0, microsecond=0)
                if target_time < now:
                    target_time = target_time.replace(year=now.year + 1)
            else:
                h, m = map(int, time_str.split(":"))
                target_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if target_time < now:
                    target_time = target_time + datetime.timedelta(days=1)
                    
            delay = (target_time - now).total_seconds()
            if delay <= 0:
                await update.message.reply_text("❌ Khung giờ này qua mất rồi! Cậu nhập lại giờ khác giúp tớ nhé:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]]))
                return
                
            sched_info = waiting_for_schedule_time.pop(user_id)
            
            job_data = {
                "chat_id": update.message.chat_id,
                "type": sched_info["type"],
                "target_platform": sched_info["target_platform"]
            }
            
            context.job_queue.run_once(execute_scheduled_job, delay, data=job_data, name=f"Job_{user_id}_{int(now.timestamp())}")
            
            await update.message.reply_text(
                f"✅ Đã lên lịch thành công!\n"
                f"⏰ Thời gian đăng: {target_time.strftime('%H:%M %d/%m/%Y')}\n\n"
                f"Tớ sẽ tự động chạy vào lúc đó. Cậu có thể gõ /jobs để xem lại lịch nha.\n"
                f"⚠️ Lưu ý: Nhớ để máy tính luôn mở nhé!",
                reply_markup=main_menu_keyboard()
            )
        except Exception as e:
            await update.message.reply_text("❌ Cậu gõ sai định dạng thời gian mất rồi. Hãy gõ lại (VD: 15:30 hoặc 15:30 25/10):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Hủy", callback_data="cancel_edit")]]))
        return
    
    # User dang cho nhap caption
    if user_id in waiting_for_caption:
        base_name = waiting_for_caption.pop(user_id)
        
        # Kiem tra xem nhom video hoac file co ton tai khong
        files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        groups = group_videos(files)
        
        if base_name not in groups and not os.path.exists(os.path.join(VIDEO_DIR, base_name)):
            await update.message.reply_text(f"Ơ... Nhóm video '{base_name}' chạy đi đâu mất rồi...", reply_markup=main_menu_keyboard())
            return
        
        # Luu caption goc (chua co hashtag) de tuy chinh theo nen tang sau
        waiting_for_platform[user_id] = {"file_path": base_name, "caption": text.strip()}
        
        short_name = base_name[:25] + "..." if len(base_name) > 25 else base_name
        
        await update.message.reply_text(
            f"📝 Nhóm: {short_name}\n"
            f"📝 Caption: {text.strip()}\n"
            f"📝 TikTok sẽ thêm: {DEFAULT_HASHTAGS}\n"
            f"📝 Facebook & YouTube giữ nguyên: {text.strip()}\n\n"
            f"Cậu muốn đăng lên đâu?",
            reply_markup=platform_keyboard(base_name, text.strip())
        )
        return
    
    if text.startswith('/post'):
        parts = text[5:].strip().split(' ', 1)
        if not parts or not parts[0]:
            await update.message.reply_text("❌ Cậu gõ sai cú pháp rồi! Nhớ gõ: /post tên_video.mp4 caption nhé.", reply_markup=main_menu_keyboard())
            return
        filename = parts[0].strip()
        user_caption = parts[1].strip() if len(parts) > 1 else ""
        file_path = os.path.join(VIDEO_DIR, filename)
        if not os.path.exists(file_path):
            await update.message.reply_text(f"❌ Tớ tìm mãi mà không thấy file '{filename}' đâu cả!", reply_markup=main_menu_keyboard())
            return
        caption = build_caption(user_caption) if user_caption else build_caption(os.path.splitext(filename)[0])
        waiting_for_platform[user_id] = {"file_path": file_path, "caption": caption}
        await update.message.reply_text(
            f"📝 Caption: {caption}\n\nCậu muốn đăng lên đâu?",
            reply_markup=platform_keyboard(file_path, caption)
        )
    elif not text.startswith('/'):
        text_lower = text.lower()
        
        # 1. Kiem tra video / trang thai
        kw_check = ["có video", "còn video", "kiểm tra", "thư mục", "xem video", "check", "còn file", "có gì không", "xem giúp", "list", "danh sách", "kiểm kê", "xem nào", "có file", "mấy video", "bao nhiêu video", "còn cái nào", "có gì mới", "tình hình", "thế nào rồi", "tiến độ"]
        
        # 2. Yeu cau dang bai / upload
        kw_post = ["đăng bài", "đăng đi", "up video", "post đi", "đăng thôi", "lên bài", "đăng giúp", "post giúp", "đăng nhé", "bắt đầu đăng", "tiến hành", "chạy đi", "run", "start", "upload", "đăng hết", "đăng toàn bộ", "chiến thôi", "triển đi", "làm việc đi"]
        
        # 3. Chao hoi
        kw_greet = ["chào", "hi", "hello", "xin chào", "alo", "chào buổi sáng", "chào buổi tối", "chào buổi chiều", "ê", "helo", "có ai không", "bot ơi", "mahiru", "ơi"]
        
        # 4. Khen ngoi
        kw_praise = ["ngoan", "giỏi", "tuyệt vời", "tốt lắm", "đỉnh", "xịn", "vip", "ngon", "xuất sắc", "đẹp", "giỏi lắm", "làm tốt lắm", "được đấy", "hay", "10 điểm", "perfect"]
        
        # 5. Cam on
        kw_thanks = ["cảm ơn", "thank", "tks", "thanks", "đa tạ", "cám ơn", "biết ơn"]
        
        # 6. Tinh cam / treu gheo
        kw_love = ["nhớ", "thương", "yêu", "thích tớ", "vợ", "cưới", "hôn", "ôm", "đẹp trai", "đẹp gái", "xinh", "dễ thương", "cute"]
        
        # 7. Hỏi han
        kw_ask = ["đang làm gì", "làm gì đó", "khỏe không", "sao rồi", "thế nào", "mệt không", "rảnh không", "bận không", "ổn không"]
        
        # 8. Xin loi
        kw_apology = ["xin lỗi", "sorry", "sr", "tha lỗi", "lỡ", "nhầm", "quên"]
        
        # 9. Met moi / than van tu user
        kw_tired = ["mệt", "chán", "buồn", "đuối", "khổ", "áp lực", "stress"]
        
        # 10. Chui the / mang bot
        kw_bad = ["ngu", "gà", "tệ", "chậm", "lag", "đần", "hư", "vớ vẩn", "tức", "điên"]
        
        # 11. Dung dang video
        kw_stop = ["dừng", "ngừng", "stop", "đừng đăng", "thôi", "hủy", "cancel", "tạm dừng"]
        kw_bad = ["ngu", "gà", "tệ", "chậm", "lag", "đần", "hư", "vớ vẩn", "tức", "điên"]
        
        if any(w in text_lower for w in kw_check):
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await update.message.reply_text("Hiện tại thư mục đang trống trơn... Cậu chưa tải thêm video nào về sao?", reply_markup=main_menu_keyboard())
            else:
                await update.message.reply_text(f"Trong thư mục hiện đang có {len(files)} video chờ cậu xử lý đấy. Cậu gõ /list để xem chi tiết nhé!", reply_markup=main_menu_keyboard())
                
        elif any(w in text_lower for w in kw_post):
            await update.message.reply_text("Tớ biết rồi, nhưng cậu muốn đăng video nào cơ? Hãy gõ /list để chọn hoặc bấm Đăng toàn bộ nhé.", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_greet):
            await update.message.reply_text("Chào cậu... Hôm nay cậu lại mang video đến cho tớ đăng giúp phải không? Cứ giao cho tớ nhé.", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_praise):
            await update.message.reply_text("Fufu... Tớ chỉ làm những việc nên làm thôi. Cậu không cần phải khen tớ quá thế đâu...", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_thanks):
            await update.message.reply_text("Không có chi đâu... Tớ giúp được cậu là vui rồi.", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_love):
            await update.message.reply_text("C-Cậu đang nói ngốc nghếch gì thế hả! Lo làm việc đi, còn bao nhiêu video chưa đăng kìa!", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_ask):
            await update.message.reply_text("Tớ đang dọn dẹp lại mấy cái thư mục video của cậu đây. Cậu bừa bộn quá đấy nhé...", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_apology):
            await update.message.reply_text("Không sao đâu, tớ hiểu mà. Cậu cứ cẩn thận hơn vào lần sau là được.", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_tired):
            await update.message.reply_text("Cậu mệt rồi sao? Cứ nghỉ ngơi đi nhé, việc tự động đăng video hãy để tớ lo hết cho.", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_bad):
            await update.message.reply_text("Tớ đang cố gắng hết sức mà... Cậu đừng mắng tớ như vậy chứ...", reply_markup=main_menu_keyboard())
            
        elif any(w in text_lower for w in kw_stop):
            stop_posting_flags[update.message.chat_id] = True
            await update.message.reply_text("🛑 Tớ nhận lệnh rồi! Tớ sẽ dừng toàn bộ quá trình đăng video ngay khi hoàn thành xong tiến trình hiện tại nhé.", reply_markup=main_menu_keyboard())
            
        else:
            await update.message.reply_text(
                "Ưm... Tớ không hiểu ý cậu lắm. Nếu muốn tớ làm gì, cậu dùng lệnh hoặc bấm nút bên dưới giúp tớ nhé.",
                reply_markup=main_menu_keyboard()
            )

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.mp4', '.mov', '.avi')):
            # Ignor part files created by splitter
            if "_part" in os.path.basename(event.src_path):
                return
            
            # Wait a bit for the file to finish copying
            time.sleep(2)
            
            # Run coroutine to notify
            if admin_chat_id and application_instance:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.notify_new_video(event.src_path))
                loop.close()
                
    async def notify_new_video(self, filepath):
        filename = os.path.basename(filepath)
        await application_instance.bot.send_message(
            admin_chat_id, 
            f"👀 Ting ting! Tớ thấy cậu vừa thả video mới vào này:\n👉 *{filename}*\n\nCậu có thể mở WebApp hoặc gõ /list để bắt đầu hẹn giờ đăng luôn nhé!",
            parse_mode="Markdown"
        )

import time
def start_watchdog():
    observer = Observer()
    event_handler = VideoHandler()
    observer.schedule(event_handler, VIDEO_DIR, recursive=False)
    observer.start()

def main() -> None:
    global application_instance
    print("Dang khoi dong Bot Mahiru...")
    application = Application.builder().token(TOKEN).post_init(set_commands).build()
    application_instance = application
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_videos))
    application.add_handler(CommandHandler("webapp", webapp_command))
    application.add_handler(CommandHandler("jobs", jobs_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Start watchdog
    threading.Thread(target=start_watchdog, daemon=True).start()
    
    print("Bot Mahiru dang chay! (TikTok + Facebook + Watchdog)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
