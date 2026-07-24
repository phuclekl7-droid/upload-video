import re

bot_path = 'bot.py'
with open(bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update post_all_task signature
old_sig = 'async def post_all_task(chat_id, context, files, target_platform="all", is_split=False, split_parts=5, base_name=None):'
new_sig = 'async def post_all_task(chat_id, context, files, target_platform="all", is_split=False, split_parts=5, base_name=None, custom_caption=None):'
content = content.replace(old_sig, new_sig)

# 2. Update post_all_task call in start_group|
old_call = 'asyncio.create_task(post_all_task(query.message.chat_id, context, target_files, platform, is_split=is_split, split_parts=split_parts, base_name=base_name))'
new_call = 'asyncio.create_task(post_all_task(query.message.chat_id, context, target_files, platform, is_split=is_split, split_parts=split_parts, base_name=base_name, custom_caption=raw_caption))'
content = content.replace(old_call, new_call)

# 3. Restructure post_all_task loop
old_loop_start = """    for original_f in files:
        if stop_posting_flags.get(chat_id):
            await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
            return
            
        original_file_path = os.path.join(VIDEO_DIR, original_f)
        
        if is_split:
            await context.bot.send_message(chat_id, f"🔪 Tớ đang cặm cụi cắt video {original_f} thành {split_parts} phần...")
            loop = asyncio.get_running_loop()
            split_files = await loop.run_in_executor(None, video_tools.split_video, original_file_path, split_parts)
        else:
            split_files = [original_file_path]
            
        for file_path in split_files:"""

new_loop_start = """    for original_f in files:
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
            thumb_msg = "\\n🖼️ Dùng ảnh bìa nhóm" if thumb_fb_yt else ""
            await context.bot.send_message(chat_id, f"🔴 Tớ đang tải bản FULL của {original_f} lên YouTube...\\n📝 Caption: {base_cap}{thumb_msg}")
            
            if thumb_fb_yt:
                rc3, stdout3, stderr3 = await run_uploader("youtube_uploader.py", original_file_path, base_cap, yt_vis, thumb_path=thumb_fb_yt)
            else:
                rc3, stdout3, stderr3 = await run_uploader("youtube_uploader.py", original_file_path, base_cap, yt_vis)
            result_yt = f"✅ YouTube ({yt_vis}): Thành công!" if rc3 == 0 else f"❌ YouTube ({yt_vis}): Thất bại"
            await context.bot.send_message(chat_id, f"📊 Kết quả YouTube '{original_f}':\\n{result_yt}")
            
            if stop_posting_flags.get(chat_id):
                await context.bot.send_message(chat_id, "🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!")
                return
        
        if is_split:
            await context.bot.send_message(chat_id, f"🔪 Tớ đang cặm cụi cắt video {original_f} thành {split_parts} phần...")
            loop = asyncio.get_running_loop()
            split_files = await loop.run_in_executor(None, video_tools.split_video, original_file_path, split_parts)
        else:
            split_files = [original_file_path]
            
        for file_path in split_files:"""
content = content.replace(old_loop_start, new_loop_start)


# 4. Remove YouTube part from inner loop
old_yt_inner = """            # Chay YouTube
            if "youtube" in target_platform or "all" in target_platform:
                yt_vis = "UNLISTED" if "unlisted" in target_platform else "PUBLIC"
                if thumb_fb_yt:
                    rc3, stdout3, stderr3 = await run_uploader("youtube_uploader.py", file_path, fb_caption, yt_vis, thumb_path=thumb_fb_yt)
                else:
                    rc3, stdout3, stderr3 = await run_uploader("youtube_uploader.py", file_path, fb_caption, yt_vis)
                result_yt = f"✅ YouTube ({yt_vis}): Thành công!" if rc3 == 0 else f"❌ YouTube ({yt_vis}): Thất bại"
            else:
                result_yt = "⏭️ YouTube: Bỏ qua"
        
        await context.bot.send_message(chat_id, f"📊 Kết quả '{f}':\\n\\n{result_tt}\\n{result_fb}\\n{result_yt}")"""

new_yt_inner = """        await context.bot.send_message(chat_id, f"📊 Kết quả phần '{f}':\\n\\n{result_tt}\\n{result_fb}")"""

# Wait, `raw_caption` in the inner loop needs to be updated too
old_caption_gen = """            f = os.path.basename(file_path)
            raw_caption = os.path.splitext(f)[0]
            tiktok_caption = build_caption(raw_caption)
            fb_caption = raw_caption"""

new_caption_gen = """            f = os.path.basename(file_path)
            raw_caption = base_cap if not is_split else os.path.splitext(f)[0]
            tiktok_caption = build_caption(raw_caption)
            fb_caption = raw_caption"""

content = content.replace(old_yt_inner, new_yt_inner)
content = content.replace(old_caption_gen, new_caption_gen)

with open(bot_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched successfully!")
