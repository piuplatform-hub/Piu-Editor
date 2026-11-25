# Từ hôm nay — Bản thử Remotion + GSAP

[Mở MP4 V003](../previews/v003/tu-hom-nay-v003-remotion.mp4) · Full HD · 50 fps · 27,44 giây

Sau phản hồi ảnh rung, dùng [bản đồ](../../../docs/REPO-MAP.md), [quy trình Remotion + GSAP + FFmpeg](../../../docs/production/workflows/footage-remotion-gsap.md) và mẫu `useGsapTimeline` của dự án Yên Thành. Remotion chia cảnh theo frame. Adapter tua timeline GSAP theo frame để ảnh, chữ và hoa chuyển động lệch nhịp. FFmpeg ghép nhạc và giải mã kiểm tra MP4.

Bốn cảnh dùng chín ảnh trong bộ 55 ảnh đã lọc. Cảnh mở tràn màn, tiếp đến khung vòm khăn voan, bộ chân dung và cảnh Song Hỷ. Vệt sáng đỏ lấy từ clip đi kèm template. Cảnh Song Hỷ bắt đầu ở 19,28 giây, tương ứng 52,36 giây trong nhạc “Ngày Đầu Tiên”.

Đã xuất 1.372 khung với mốc thời gian cách nhau 20 ms. Khung 66 có cùng SHA-256 khi render lại sau khi tua qua các cảnh theo thứ tự khác. Đã xem 14 khung trích từ MP4, giải mã toàn bộ hình và tiếng, và đo nhạc −18,35 LUFS, đỉnh −10,55 dBTP. Chưa kiểm tra cảm giác khi phát trên thiết bị chiếu. Bản này thử kỹ thuật và hướng chuyển cảnh cho slideshow.

Từ thư mục dự án, dùng `npm ci` theo lockfile, `python -B -X utf8 src/v003/prepare.py`, `npm run preview:stills` và `npm run preview:render`. [Timeline](../src/v003/timeline.json) · [Bảng khung từ MP4](../previews/v003/preview-board.jpg) · [Bằng chứng](../../../docs/production/evidence/2026-11-25-wedding-slideshow-v003-preview.json)
