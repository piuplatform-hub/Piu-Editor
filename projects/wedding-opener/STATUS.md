# Trạng thái — Từ hôm nay

**Đã xuất và kiểm tra V001 · 25/11/2026**

Bản mở màn dài 86,4 giây, Full HD 1920 × 1080, 30 fps. Thẻ kết dùng ảnh hai bạn và lời cảm ơn. [MP4 V001](../../output/wedding-opener/tu-hom-nay-v001.mp4) · [Thông tin bàn giao](../../output/wedding-opener/delivery.md)

Đã giải mã toàn bộ file, kiểm tra âm thanh bằng phép đo và xem khung ở cả 16 điểm chuyển cảnh. Chưa nghe trực tiếp hoặc xem liên tục trên thiết bị chiếu. [QA V001](notes/qa.md)

## Phương án tĩnh ban đầu · 25/11/2026

Đã khảo sát ảnh và nhạc ở `D:\Edit Video Cuoi`, tham khảo mẫu mở màn và xuất [bảng bốn khung tĩnh](previews/storyboard-v001.png). [Brief](brief.md) mô tả bố cục phim 80 giây và [shot list](notes/shot-list.md) ghi các ảnh ứng viên theo cảnh. [Manifest](assets.json) có SHA-256 của năm ảnh được dùng trong bảng và bài nhạc đề xuất.

Bảng tĩnh dùng để thử bố cục từ khung ngà sang Song Hỷ, chọn chữ tiếng Việt và chuẩn bị căn điểm cắt theo “Ngày Đầu Tiên”.

## Dựng V001 · 25/11/2026

Người dùng chọn phương án “Từ hôm nay”. Đã dựng timeline 20 ảnh, 17 cảnh và ghép nhạc “Ngày Đầu Tiên” từ MP3 được cung cấp. Timeline V001 dài 86,4 giây để giữ nhịp kết bài. Dùng ảnh cận và lời cảm ơn nếu tên, ngày cưới chưa được gửi.

Lệnh từ thư mục dự án là `npm run prepare:media`, `npm run stills`, `npm run render` và `npm run qa`. Chi tiết điểm cắt nằm trong [timeline](src/timeline.json).
