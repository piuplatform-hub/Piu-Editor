# Từ hôm nay — Kịch bản bản thử V004

Đoạn 47,04 giây dùng 12 ảnh đã lọc và nhạc “Ngày Đầu Tiên”. Mạch đi từ lời mở nhẹ trên ảnh tràn màn, qua những khoảnh khắc bên nhau rồi đến Song Hỷ và lời cảm ơn khách mời.

| Thời gian | Hình ảnh | Chữ và chuyển động |
|---|---|---|
| 00:00–00:07,64 | Hai bạn cạnh bàn tiệc, ảnh tràn khung với nhịp máy lùi nhẹ. | “Từ hôm nay” hiện lần lượt theo hai dòng từ 00:00,70. Đường kẻ mảnh theo sau. Chữ rời từ 00:06,24. |
| 00:07,64–00:15,44 | Mở khung vòm khăn voan, ghép cùng ảnh cận. Hoa nhỏ chuyển động ở mép dưới. | “Mình chọn nhau” lên từ 00:08,86. Giữ chữ đủ lâu để đọc rồi tan dần từ 00:14,00. |
| 00:15,44–00:24,56 | Ba ảnh chân dung mở ra lệch nhịp như các trang album. | Hình và nhạc dẫn cảnh. |
| 00:24,56–00:33,84 | Cận cảnh ở bàn tiệc và khoảnh khắc nâng ly. | Hai lớp ảnh trôi nhẹ trên nền sáng. |
| 00:33,84–00:40,92 | Vệt sáng ấm chuyển sang hai ảnh Song Hỷ. | “Ngày chung đôi” hiện từ 00:34,82 rồi rời chữ từ 00:39,56. Hai dòng ngày cưới bắt đầu xuất hiện ở 00:35,20. |
| 00:40,92–00:47,04 | Tông ngà trở lại với hai ảnh cưới, nhạc hạ dần. | “Cảm ơn” và “đã đến chung vui” vào từ 00:41,88, tan dần từ 00:46,00. Ngày cưới còn ở góc dưới bên phải đến hết. |

## Ngày cưới

Thẻ góc dưới bên phải hiện **29/11/2026 Dương lịch** và **21/10/2026 Âm lịch**. Số ngày lớn hơn nhãn lịch, trên nền nâu rượu để dễ đọc ở cả đoạn Song Hỷ và đoạn sáng.

Chữ tiêu đề dùng Cormorant Garamond, nhãn ngày và câu phụ dùng Be Vietnam Pro. Chuyển động chữ dùng độ mờ và dịch chuyển nhẹ theo cụm. Các cảnh, chữ và nhạc cùng dùng timeline 50 fps. [Mốc dựng](../src/v004/timeline.json)

## Bản thử đã xuất

[Mở MP4 V004](../previews/v004/tu-hom-nay-v004-text.mp4) · 1920 × 1080 · 50 fps · H.264 và AAC stereo

Đã giải mã toàn bộ 2.352 khung và track âm thanh. Xem 21 khung trích từ MP4, gồm các pha vào, giữ và ra của chữ. Đối chiếu hai dòng ngày cưới trên nền Song Hỷ ở 36,80 giây và nền sáng ở 43,86 giây. Âm thanh đo −18,96 LUFS, đỉnh −10,40 dBTP. Khung 129 render lại sau khi tua không tuần tự có cùng SHA-256. Chưa thử phát trên thiết bị tại tiệc.

Từ thư mục dự án, chạy `python -B -X utf8 src/v003/prepare.py v004`, `npm run preview:v004:stills` và `npm run preview:v004:render`. [Các pha chữ từ MP4](../previews/v004/preview-board.jpg) · [Góc ngày cưới từ MP4](../previews/v004/wedding-date-from-mp4.jpg) · [Bằng chứng QA](../../../docs/production/evidence/2026-11-25-wedding-slideshow-v004-preview.json)
