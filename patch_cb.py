import os
import re

bot_path = 'bot.py'
with open(bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add hashlib and callback_map if not there
if "callback_map = {}" not in content:
    content = content.replace("stop_posting_flags = {}", "stop_posting_flags = {}\ncallback_map = {}\nimport hashlib\n\ndef get_callback_id(text):\n    h = hashlib.md5(text.encode('utf-8')).hexdigest()[:16]\n    callback_map[h] = text\n    return h\n")

# Fix list_videos
old_list_videos = """        buttons = []
        for base_name in groups:
            short_name = base_name[:25] + "..." if len(base_name) > 25 else base_name
            buttons.append([InlineKeyboardButton(f"✅ Chọn nhóm '{short_name}'", callback_data=f"edit_name|{base_name}")])"""
new_list_videos = """        buttons = []
        for base_name in groups:
            short_name = base_name[:25] + "..." if len(base_name) > 25 else base_name
            cb_id = get_callback_id(base_name)
            buttons.append([InlineKeyboardButton(f"✅ Chọn nhóm '{short_name}'", callback_data=f"edit_name|{cb_id}")])"""
content = content.replace(old_list_videos, new_list_videos)

# Fix cmd_list
old_cmd_list = """    if data == "cmd_list":
        try:
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await query.edit_message_text(f"Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé.\\n{VIDEO_DIR}", reply_markup=main_menu_keyboard())
                return
            msg = "Video đang chờ đăng:\\n\\n"
            for i, f in enumerate(files, 1):
                msg += f"{i}. {f}\\n"
            msg += f"\\nHashtag mặc định: {DEFAULT_HASHTAGS}"
            buttons = []
            for f in files:
                short_name = f[:25] + "..." if len(f) > 25 else f
                buttons.append([InlineKeyboardButton(f"✏️ Sửa tên '{short_name}'", callback_data=f"edit_name|{f}")])
            buttons.append([InlineKeyboardButton("🚀 Đăng TOÀN BỘ (Lấy tên file làm Caption)", callback_data="post_all_menu")])
            buttons.append([InlineKeyboardButton("📖 Hướng dẫn", callback_data="cmd_help")])
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await query.edit_message_text(f"Lỗi: {e}", reply_markup=main_menu_keyboard())"""
            
new_cmd_list = """    if data == "cmd_list":
        try:
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await query.edit_message_text(f"Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé.\\n{VIDEO_DIR}", reply_markup=main_menu_keyboard())
                return
            groups = group_videos(files)
            
            msg = "Tớ tìm thấy rồi. Video đang chờ đăng:\\n\\n"
            for i, (base_name, group_files) in enumerate(groups.items(), 1):
                thumb = ""
                for ext in ['.jpg', '.png']:
                    if os.path.exists(os.path.join(VIDEO_DIR, f"{base_name}{ext}")):
                        thumb = " 🖼️"
                        break
                msg += f"{i}. Nhóm <code>{base_name}</code> ({len(group_files)} tập){thumb}\\n"
            msg += f"\\nHashtag mặc định: {DEFAULT_HASHTAGS}\\nBấm 'Chọn nhóm' để đặt lệnh đăng."
            
            buttons = []
            for base_name in groups:
                short_name = base_name[:25] + "..." if len(base_name) > 25 else base_name
                cb_id = get_callback_id(base_name)
                buttons.append([InlineKeyboardButton(f"✅ Chọn nhóm '{short_name}'", callback_data=f"edit_name|{cb_id}")])
            buttons.append([InlineKeyboardButton("🚀 Đăng TOÀN BỘ tất cả", callback_data="post_all_menu")])
            buttons.append([InlineKeyboardButton("📖 Hướng dẫn", callback_data="cmd_help")])
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
        except Exception as e:
            await query.edit_message_text(f"Lỗi: {e}", reply_markup=main_menu_keyboard())"""
content = content.replace(old_cmd_list, new_cmd_list)

# Fix edit_name handling
old_edit_name = """    elif data.startswith("edit_name|"):
        base_name = data.split("|", 1)[1]"""
new_edit_name = """    elif data.startswith("edit_name|"):
        cb_id = data.split("|", 1)[1]
        base_name = callback_map.get(cb_id, cb_id) # fallback to cb_id if it was a real name before restart"""
content = content.replace(old_edit_name, new_edit_name)

with open(bot_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched successfully!")
