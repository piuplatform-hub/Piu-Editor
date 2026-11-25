# Từ hôm nay — Slideshow V005

Ngày 25/11/2026. Từ bản demo đã duyệt hướng chuyển động và chữ, dựng 13 chương nhạc, 261 cảnh và 28 cụm chữ cho bản chiếu tiệc dài 45 phút 52,92 giây. Dùng 54 ảnh riêng biệt từ bộ 55 tệp đã lọc. Sắp ảnh hai bé ở đầu và nối lại với ảnh cưới trong chương “Photograph”.

- Khóa danh sách nhạc bằng hash đầu vào và đặt mốc theo frame. Phát đủ 13 file theo thứ tự người dùng gửi. Đã dịch 224 mốc hình nội bộ tới gần điểm nhấn đo được trong audio. Kịch bản dành chỗ cho cả các cảnh có chữ và đoạn chỉ có hình với nhạc.
- Dùng Remotion để tạo lớp chữ với font Việt. Khi kết xuất nhiều cụm, chọn composition với đúng inputProps cho từng cụm. GSAP lấy mẫu vào/ra ở 50 fps. OpenCV ghép theo tọa độ phần lẻ, tránh bước nhảy do làm tròn lớp ảnh theo pixel nguyên.
- Xuất từng chương bằng PyAV/NVENC. FFmpeg ghép nhạc, PyAV gắn chapter. Đối chiếu 13 mốc, 137.646 khung và gói AAC sau ghép. Giải mã toàn bộ, xem khung ở từng cảnh và kiểm tra chữ từ MP4.

Đã đo −18,04 LUFS và −6,07 dBTP. Chưa nghe trực tiếp hoặc xem liên tục trên thiết bị tại tiệc. [Kịch bản](../../../projects/wedding-slideshow/notes/kich-ban-v005.md) · [QA](../../../projects/wedding-slideshow/notes/qa.md) · [Bằng chứng](../evidence/2026-11-25-wedding-slideshow-v005.json)

Người dùng đã xem và phản hồi video đẹp. [Quy trình slideshow ảnh](../workflows/photo-slideshow.md) · [Hướng dẫn tái tạo V005](../../../projects/wedding-slideshow/notes/tai-tao-v005.md)
