import os

bot_path = 'bot.py'
with open(bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '🛑 Đã dừng tiến trình đăng tự động theo yêu cầu của cậu!': '🛑 Tớ đã dừng việc đăng tự động theo lời cậu rồi nhé!',
    '🔪 Đang cắt video': '🔪 Tớ đang cặm cụi cắt video',
    '🚀 Đang tự động đăng:': '🚀 Tớ đang bắt đầu đăng:',
    '🎉 Tớ đã đăng xong toàn bộ video rồi nhé!': '🎉 Fufu, tớ đã đăng xong toàn bộ video cho cậu rồi đấy! Cậu vất vả rồi!',
    'Đến giờ hẹn nhưng thư mục đang trống': 'Đến giờ hẹn rồi mà thư mục lại trống trơn... Cậu quên bỏ video vào đúng không',
    'Lỗi hẹn giờ:': 'Ưm... Có lỗi hẹn giờ mất rồi:',
    'Không có lịch hẹn nào đang chờ.': 'Hiện tại không có lịch hẹn nào đang chờ cả, cậu à.',
    '🟢 Hệ thống bình thường. Sẵn sàng đăng TikTok + Facebook.': '🟢 Hệ thống vẫn ổn định. Tớ luôn sẵn sàng đăng TikTok và Facebook cho cậu.',
    'Thư mục đang trống...': 'Thư mục đang trống trơn... Cậu mau thêm video vào để tớ còn làm việc nhé.',
    '🟢 Hệ thống bình thường.': '🟢 Mọi thứ vẫn ổn cả.',
    'Tớ đã sẵn sàng.\\nThư mục:': 'Tớ đã chuẩn bị sẵn sàng rồi đây.\\nThư mục hiện tại:',
    'Đã hủy. Cậu muốn làm gì tiếp?': 'Tớ đã hủy lệnh rồi. Cậu muốn tớ làm gì tiếp theo nào?',
    'Cậu muốn đăng toàn bộ': 'Cậu muốn tớ đăng toàn bộ',
    'Cậu có muốn CẮT toàn bộ video': 'Cậu có muốn tớ CẮT các video này',
    '🛑 Đang ra lệnh dừng... Tớ sẽ dừng lại sau khi đăng xong video hiện tại nhé.': '🛑 Tớ nhận lệnh rồi... Tớ sẽ dừng lại ngay sau khi đăng xong video hiện tại nhé.',
    'Hết hạn rồi, cậu làm lại từ /list nhé.': 'Ưm... Hết thời gian chờ mất rồi. Cậu thao tác lại từ /list giúp tớ nhé.',
    'Cậu có muốn CẮT nhóm video này thành nhiều phần trước khi đăng không?': 'Cậu có muốn tớ CẮT nhóm video này ra thành nhiều phần nhỏ không?',
    '🎵 Đang đăng nhóm': '🎵 Tớ đang cặm cụi đăng nhóm',
    '📘 Đang đăng nhóm': '📘 Tớ đang tải nhóm',
    '🔴 Đang đăng nhóm': '🔴 Tớ đang tải nhóm',
    '🚀 Đang đăng nhóm': '🚀 Tớ đang tải nhóm',
    "❌ Chức năng Giao diện WebApp chỉ dùng được khi nhắn tin RIÊNG tư với tớ! Cậu hãy click vào tên tớ, chọn 'Send Message' (Nhắn tin) và gõ lại lệnh /webapp nhé.": "❌ Chức năng WebApp xịn xò này chỉ dùng được khi cậu nhắn tin RIÊNG với tớ thôi! Cậu vào hòm thư riêng nhắn cho tớ nhé.",
    '⏳ Máy chủ WebApp đang khởi động, vui lòng thử lại sau vài giây...': '⏳ Máy chủ WebApp đang rục rịch khởi động, cậu đợi tớ vài giây rồi thử lại nha...',
    'Bấm vào nút bên dưới để mở giao diện WebApp cực xịn nhé!': 'Cậu bấm vào nút bên dưới để mở giao diện WebApp tớ vừa chuẩn bị nhé!',
    '❌ Thời gian hẹn đã qua mất rồi!': '❌ Thời gian cậu hẹn đã trôi qua mất rồi!',
    'Cậu có thể gõ /jobs để xem.': 'Cậu có thể gõ /jobs để xem lại lịch nha.',
    '❌ Thời gian đã qua! Cậu nhập lại nhé:': '❌ Khung giờ này qua mất rồi! Cậu nhập lại giờ khác giúp tớ nhé:',
    '❌ Lỗi định dạng thời gian. Hãy gõ lại đúng định dạng': '❌ Cậu gõ sai định dạng thời gian mất rồi. Hãy gõ lại',
    "File '{filename}' không còn nữa...": "Ơ... File '{filename}' chạy đi đâu mất rồi...",
    '❌ Sai cú pháp! Gõ: /post tên_video.mp4 caption': '❌ Cậu gõ sai cú pháp rồi! Nhớ gõ: /post tên_video.mp4 caption nhé.',
    "❌ Không thấy file '{filename}'!": "❌ Tớ tìm mãi mà không thấy file '{filename}' đâu cả!",
    '👀 Ting ting! Tớ phát hiện sếp vừa thả video mới vào thư mục:': '👀 Ting ting! Tớ thấy cậu vừa thả video mới vào này:',
    'Tớ đang phân tích và tạo ảnh bìa, đợi tí nhé...': 'Tớ đang xem xét và chuẩn bị ảnh bìa, cậu chịu khó đợi tớ một tẹo nhé...',
    'Đang tự động đăng:': 'Tớ đang tự động đăng:'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(bot_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Da patch xong bot.py')
