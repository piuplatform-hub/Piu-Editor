# Tổng kết — Từ hôm nay

Project `wedding-opener` đã giao V001 ngày 25/11/2026.

Áp dụng [cách lưu kinh nghiệm sản xuất](../../../docs/production/README.md). Điền sau một bản giao hoặc vòng phản hồi đáng kể; ghi rõ điều chưa kiểm tra.

## Mục tiêu và kết quả

- Phim mở màn tiệc cưới đi từ album ảnh tông ngà sang chương Song Hỷ rồi về thẻ cảm ơn. Bản V001 dùng 20 ảnh, 17 cảnh và nhạc “Ngày Đầu Tiên” từ nguồn đã có.
- Bản giao là MP4 1920 × 1080, 30 fps, 86,4 giây. Remotion 4.0.540 dựng phần hình. FFmpeg n7.1 chuẩn bị, ghép và đo âm thanh. [Bản giao và lệnh tái tạo](../../../output/wedding-opener/delivery.md)

## Phản hồi của người dùng

- Trước khi có MP4, người dùng duyệt phương án “Từ hôm nay”, báo phiên cũ lỗi `Audio input is not available` và yêu cầu tiếp tục. Phiên tiếp nối xuất thành công bản dựng V001 đã lưu.
- Thẻ kết dùng lời cảm ơn mặc định. Hồ sơ dựng chưa có tên hoặc ngày cưới.
- Sau khi xem, người dùng thấy bản mở màn khá ổn, còn nhiều khoảng trống và muốn dùng thêm các bài trong danh sách. Người dùng yêu cầu slideshow dài để chiếu lúc ăn tiệc, có thể lấy thêm ảnh hoặc đổi hiệu ứng khi ảnh xuất hiện lại. [Brief của bản chiếu tiệc](../../wedding-slideshow/brief.md)

## Bài học có thể dùng lại

| Điều kiện / vấn đề | Nguyên nhân đã xác nhận hoặc giả thuyết | Cách xử lý | Kết quả và bằng chứng | Giới hạn |
|---|---|---|---|---|
| Phiên dựng cũ dừng trong lúc xuất | Codex nhận kết quả nghe thử dạng `input_audio` rồi báo `audio_input_unavailable`. Lệnh xuất báo riêng `write EOF` ở mốc 70% phần hình chính. | Đối chiếu tiến trình và các đường dẫn đầu ra trước khi chạy lại bằng script cũ. | Đã xuất đủ 2.592 khung và ghi kết quả QA từ MP4. | Chưa xác định quan hệ giữa lỗi phiên chat và lỗi ghi của lần xuất cũ. |
| Cần xác minh nhạc và đoạn nối sau gián đoạn | QA cần dựa trên bản đã ghép hình và tiếng. | Giải mã MP4, đo AAC, đối chiếu với WAV và lấy mẫu ảnh ở hai phía của các điểm chuyển cảnh. | Nhạc −15,54 LUFS, gói AAC liền thời gian. Thẻ kết vào đúng mốc 76,63 giây trên mẫu đã xem. | Phép đo và khung trích chưa xác nhận trải nghiệm nghe và xem liên tục ở phòng tiệc. |

## Kiểm tra và bảo toàn

- Xem khung đầu, giữa, cuối, mẫu ở 16 điểm chuyển cảnh và chữ tiếng Việt trên ảnh trích từ MP4.
- Giải mã và đo AAC. Chưa nghe trực tiếp hoặc xem playback liên tục.
- FFprobe, giải mã hết, nhịp timestamp và 21 hash đầu vào đều đạt. Bản gốc giữ nguyên. Trước phiên này chưa có MP4 V001. [QA](qa.md)

## Bổ sung cho kho kinh nghiệm

- Lưu quy trình đối chiếu đầu ra trước khi xuất lại và các phép QA trên bản giao tại [hồ sơ khôi phục V001](../../../docs/production/cases/2026-11-25-wedding-opener-v001.md).
