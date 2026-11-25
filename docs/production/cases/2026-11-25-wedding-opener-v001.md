# Từ hôm nay — Xuất lại V001 sau gián đoạn

Ngày 25/11/2026, project `wedding-opener`. Người dùng duyệt phương án phim mở màn, thấy phiên dựng báo lỗi và yêu cầu tiếp tục.

Phiên cũ tạo được nhạc và 26 khung xem trước. Sau khi FFmpeg trích một MP3 nghe thử, công cụ đưa mẫu đó vào cuộc trò chuyện dưới dạng `input_audio`. Lượt đang làm và các tin nhắn gõ tay kế tiếp báo `audio_input_unavailable`. Lệnh render trong cùng phiên thoát mã 1 với `write EOF` sau mốc báo 70% phần hình chính. Quan hệ trực tiếp giữa hai lỗi chưa được xác định.

Phiên tiếp nối xác minh thư mục V001 chưa có MP4 hoặc hai đoạn hình trung gian và không còn tiến trình xuất. Chạy lại `npm run render` với cùng timeline, ảnh và WAV. Lệnh qua cả hai phần hình và ghép AAC thành MP4 dài 86,4 giây. QA giải mã hết file, kiểm tra đủ 2.592 khung, thời gian AAC và đo nhạc từ bản đã ghép. Xem ảnh ở hai phía của 16 biên chuyển cảnh, gồm điểm ghép thẻ cảm ơn ở 76,63 giây.

- Khi tiếp nối, kiểm tra tiến trình và file thật trước khi chạy lại. Nếu đã có bản xuất, kiểm tra file đó trước để tránh mất dấu bản cũ.
- Khi phiên gặp lỗi `audio_input_unavailable` sau kết quả nghe thử, vẫn có thể đo tiếng trực tiếp từ MP4 bằng FFmpeg và đọc báo cáo dạng văn bản. Đo thời gian, âm lượng và đối chiếu với WAV giúp phát hiện lỗi ghép. Ghi phần nghe trực tiếp thành giới hạn nếu chưa thực hiện.

Kết quả áp dụng cho V001 trên máy dựng. Chưa thử thiết bị chiếu ở tiệc, playback liên tục hoặc nghe bằng tai. [Bằng chứng V001](../evidence/2026-11-25-wedding-opener-v001.json) · [QA chi tiết](../../../projects/wedding-opener/notes/qa.md) · [Tổng kết](../../../projects/wedding-opener/notes/retrospective.md)
