# Từ hôm nay — Bản thử V002 từ mẫu ảnh cưới

Ngày 25/11/2026. Người dùng muốn bản slideshow bớt đơn điệu, gửi mẫu “Romantik Love Story” và lọc lại 55 ảnh. Đã xem tài liệu ba trang, đọc thông tin cảnh trong file AEP và kiểm tra clip ánh sáng, bokeh và PNG ở bộ mẫu. Máy dựng chưa có runtime After Effects được xác nhận để xuất project mẫu.

Khung vòm, lớp hoa và lá màu nước, chuyển bằng vệt sáng được thử trong mạch ảnh riêng. Giữ độ đầy khung với ảnh ngang tràn màn, ảnh cận và khung xếp lệch. V002 thử bằng 22 ảnh, 10 cảnh và nhạc “Ngày Đầu Tiên” trong 64,72 giây. Kiểm tra cả các khung trước, giữa và sau điểm chuyển để chỉnh crop và cường độ lớp trang trí.

Cách dùng lại gồm đối chiếu thư mục mới với bộ nguồn cũ trước khi chọn ảnh, dựng một đoạn có đủ nhóm bố cục để xem hướng thẩm mỹ, và lưu tên, hash của ảnh đã lọc theo phiên bản. Phạm vi V002 là đoạn thử. Chưa có đánh giá của người dùng về bản mới hoặc thử trên thiết bị chiếu. [Ghi chú bản thử](../../../projects/wedding-slideshow/notes/preview-v002.md) · [Bằng chứng](../evidence/2026-11-25-wedding-slideshow-preview-v002.json)

## Phản hồi về độ mượt và thử công cụ trong repo

Người dùng thấy ảnh rung khi phát. Hai vùng ảnh lấy mẫu cho thấy vị trí đứng yên qua nhiều khung rồi nhảy gần một pixel, dù MP4 có mốc thời gian đều. Bản dựng lại dùng tọa độ phần lẻ và 50 fps. Khi so cùng bước 40 ms, số lần dịch quá 0,5 pixel giảm từ 40 xuống 0 trong hai vùng. Khi kiểm tra độ mượt, đo chuyển động trong chính MP4 bên cạnh số lượng khung và PTS. [Đối chiếu V002](../evidence/2026-11-25-wedding-slideshow-v002-motion.json)

Một phép thử riêng dùng Remotion + GSAP + FFmpeg theo quy trình có sẵn. Bốn cảnh được dựng thành 27,44 giây ở 50 fps, đầy đủ hình và tiếng. Khung 66 lặp lại cùng hash sau khi tua theo thứ tự khác. Phép thử xác nhận công cụ chạy trên ảnh cưới đã lọc và hiệu ứng từ mẫu. Mức độ giống chuyển động của template cần đối chiếu với demo gốc. [Bản thử V003](../../../projects/wedding-slideshow/notes/preview-v003.md) · [Bằng chứng V003](../evidence/2026-11-25-wedding-slideshow-v003-preview.json)

## V004 — Chữ theo mạch phim và ngày cưới ở góc

Sau khi người dùng phản hồi chuyển động đã mượt hơn, V004 thử thêm cụm chữ Việt vào và ra theo cảnh. Giữ nhịp 50 fps. Đặt hai mốc ngày người dùng cung cấp trong một lớp ở góc dưới, giữ qua điểm chuyển từ nền đỏ sang nền sáng. Các cụm chữ rời trước khi đổi cảnh, dấu nằm cùng dòng chữ. Bản thử 47,04 giây giải mã toàn bộ. Kiểm tra khung trích của cả hai nền và các pha hiện chữ. Chưa thử trên màn chiếu tại tiệc. [Kịch bản và QA V004](../../../projects/wedding-slideshow/notes/kich-ban-v004.md) · [Bằng chứng V004](../evidence/2026-11-25-wedding-slideshow-v004-preview.json)
