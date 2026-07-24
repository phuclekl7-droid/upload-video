import os

bot_path = 'bot.py'
with open(bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We will replace the entire handle_text block
old_block = """    elif not text.startswith('/'):
        text_lower = text.lower()
        
        # 1. Hoi ve video / kiem tra thu muc
        if any(w in text_lower for w in ["có video", "còn video", "kiểm tra", "thư mục", "xem video", "check"]):
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
            if not files:
                await update.message.reply_text("Hiện tại thư mục đang trống trơn... Cậu chưa tải thêm video nào về sao?", reply_markup=main_menu_keyboard())
            else:
                await update.message.reply_text(f"Trong thư mục hiện đang có {len(files)} video chờ cậu xử lý đấy. Cậu gõ /list để xem chi tiết nhé!", reply_markup=main_menu_keyboard())
                
        # 2. Yeu cau dang bai
        elif any(w in text_lower for w in ["đăng bài", "đăng đi", "up video", "post đi", "đăng thôi"]):
            await update.message.reply_text("Tớ biết rồi, nhưng cậu muốn đăng video nào cơ? Hãy gõ /list để chọn nhé, hoặc nói rõ tên cho tớ biết.", reply_markup=main_menu_keyboard())
            
        # 3. Chao hoi
        elif any(w in text_lower for w in ["chào", "hi", "hello", "xin chào", "alo"]):
            await update.message.reply_text("Chào cậu... Hôm nay cậu lại mang video đến cho tớ đăng giúp phải không? Cứ giao cho tớ nhé.", reply_markup=main_menu_keyboard())
            
        # 4. Khen ngoi
        elif any(w in text_lower for w in ["ngoan", "giỏi", "cảm ơn", "tuyệt vời", "tốt lắm", "đỉnh"]):
            await update.message.reply_text("Fufu... Tớ chỉ làm những việc nên làm thôi. Cậu không cần phải khen tớ quá thế đâu...", reply_markup=main_menu_keyboard())
            
        # 5. Tinh cam
        elif any(w in text_lower for w in ["nhớ", "thương", "yêu", "thích tớ"]):
            await update.message.reply_text("C-Cậu đang nói ngốc nghếch gì thế hả! Lo làm việc đi, còn bao nhiêu video chưa đăng kìa!", reply_markup=main_menu_keyboard())
            
        # 6. Hỏi han
        elif any(w in text_lower for w in ["đang làm gì", "làm gì đó", "khỏe không", "sao rồi"]):
            await update.message.reply_text("Tớ đang dọn dẹp lại mấy cái thư mục video của cậu đây. Cậu bừa bộn quá đấy nhé...", reply_markup=main_menu_keyboard())
            
        # Mac dinh fallback
        else:
            await update.message.reply_text(
                "Ưm... Tớ không hiểu ý cậu lắm. Cậu dùng lệnh hoặc bấm nút bên dưới giúp tớ nhé.",
                reply_markup=main_menu_keyboard()
            )"""

new_block = """    elif not text.startswith('/'):
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
            
        else:
            await update.message.reply_text(
                "Ưm... Tớ không hiểu ý cậu lắm. Nếu muốn tớ làm gì, cậu dùng lệnh hoặc bấm nút bên dưới giúp tớ nhé.",
                reply_markup=main_menu_keyboard()
            )"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced successfully!")
else:
    print("Old block not found!")
