# Tổng kết — TVC Yên Thành, 03/11/2026

- Project: `tvc-driving-premium`
- Phiên bản: v001 → v004; bản người dùng phản hồi tích cực là v004.
- Mục tiêu: TVC từ footage sẵn có, text FX nổi bật và mượt, nhạc/SFX mới, bỏ tiếng gốc.
- Bản giao: v004, Full HD 24 fps, 975 frame / 40,625 giây hình; MP4 container 40,640 giây.

## Công cụ và cách làm

Remotion 4.0.540 quản lý composition/frame; GSAP 3.15.0, CustomEase và DrawSVG thực hiện animation chữ/SVG; FFmpeg/ffprobe n7.1 trong dependency chuẩn bị media, mix và kiểm tra. Hướng dẫn từ Remotion Skills và GSAP Skills. Code hiện thực ở `src/v004`; lệnh tái tạo trong [render-v004](render-v004.md).

## Phản hồi và thay đổi

- V001 chưa đủ hấp dẫn; người dùng ưu tiên chữ và hiệu ứng.
- V003 có bản xuất nhưng bị cắt dấu tiếng Việt ở 5 nhóm chữ. Người dùng gửi ảnh và yêu cầu stroke cùng xanh nước biển.
- Đã tái hiện lỗi clipPath trên span, bỏ vùng cắt cục bộ khỏi chữ, animate từ NFC; Be Vietnam Pro, stroke mảnh và màu nhấn xanh.
- Sau v004, người dùng phản hồi: “tuyệt! ổn hơn rất nhiều bạn ạ!”

## Bài học dùng lại

| Vấn đề | Nguyên nhân / xử lý | Bằng chứng | Giới hạn |
|---|---|---|---|
| Dấu bị cắt dù có font | ClipPath cắt ink vượt line box; bỏ clip/overflow cục bộ, giữ dấu cùng từ | So cùng font có/không clip; so ảnh sau dừng với reference; xem 5 vị trí từ MP4 | Vẫn cần kiểm tra font/cỡ/mask khác |
| Hai lần render trùng nhau nhưng cùng sai | Phép so v003 chỉ chứng minh tính nhất quán | Người dùng báo lỗi sau khi bài so pixel đạt | Reference phải đúng; tiếp tục kiểm tra thị giác |
| Runtime không giống ghi chú cũ | Browser đi kèm chạy được ở lượt hiện tại; binary FFmpeg có trong dependency | Native render và QA MP4 đã chạy | Chưa chứng minh clean rebuild trên máy khác |
| Văn bản ghi qua shell mất dấu | Unicode bị đổi trước khi Python ghi UTF-8 | Một số ghi chú cũ còn dấu hỏi thay dấu Việt | Tài liệu mới ghi Unicode trực tiếp và đọc lại |

## Đã kiểm tra và phần còn lại

- Đã xem ảnh thiết kế, mẫu frame animation, biên chuyển cảnh và 5 vị trí lỗi từ MP4.
- Full decode PASS, đúng preset; −14,53 LUFS / −3,60 dBTP; waveform audio khớp master.
- Hai ảnh grid chữ sau dừng trùng pixel reference không animate; 4 face mới có đủ 107 ký tự chữ đã kiểm tra.
- 8 nguyên liệu và 9 file giao trước v004 khớp hash; soundtrack master v004 giống v003.
- Trợ lý chưa nghe bằng tai hoặc xem playback liên tục. Phản hồi người dùng được ghi riêng.

## Đã lưu cho AI tiếp theo

- [Hồ sơ Yên Thành](../../../docs/production/cases/2026-11-03-yen-thanh-tvc.md)
- [Quy trình Remotion + GSAP + FFmpeg](../../../docs/production/workflows/footage-remotion-gsap.md)
- [Kiểm tra chữ tiếng Việt](../../../docs/production/quality/vietnamese-text.md)
- [Cải tiến còn cần thử](../../../docs/production/IMPROVEMENTS.md)

Ảnh trước/sau và JSON nhỏ được chép vào docs để giữ được khi cache/output không còn. Thư viện component dùng chung và tái tạo từ Source trên máy mới vẫn là đề xuất có điều kiện kiểm chứng.
