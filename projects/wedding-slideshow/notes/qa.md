# Kiểm tra chất lượng

## Bản thử

Xem 30 khung bố cục và xuất một đoạn chuyển động 15 giây. Tăng tương phản của chữ mở/kết và dùng chân dung riêng của cả cô dâu lẫn chú rể trong các cảnh tương ứng. Thử ghép hai phần hình đầu với WAV, kiểm tra được 10.074 khung, 18.890 gói AAC và các điểm seek quanh biên ghép.

## Bản giao V001

- `src/render.py final` và `src/qa.py` thoát mã 0. PyAV 17.0.1 mã hóa H.264 bằng NVENC trên RTX 3060, FFmpeg n7.1 ghép MP4 và AAC. File dài 2.007,48 giây, 774.568.622 byte.
- FFprobe xác nhận hình 1920 × 1080, 25 fps, 50.187 khung, YUV420p BT.709. Âm thanh AAC stereo 48 kHz có 94.102 gói. Hình và tiếng cùng dài 2.007,48 giây. Giải mã hết hai track và kiểm tra timestamp hình/tiếng.
- Đã xem khung giữa của cả 126 cảnh, một mẫu ở 125 điểm chuyển ảnh và 30 mẫu ở đầu, cuối và biên đổi bài. Ảnh được đặt sát mép, viền mảnh. Chữ “Từ hôm nay” và “Cảm ơn” hiện đủ dấu trên các khung Full HD.
- Đo AAC −18,03 LUFS và −5,04 dBTP. Đối chiếu WAV và AAC tại hai đoạn mỗi bài, tương quan thấp nhất 0,99890. Phát hiện 0 khoảng dưới −48 dBFS kéo dài từ 0,7 giây và xác nhận đoạn cuối đã hạ nhạc.
- 176 ảnh và 10 MP3 dùng trong bản chiếu có hash khớp bản gốc. Tệp ảnh ghi thứ tự phát cũng đã đối chiếu.
- Hình được xem theo khung trích. Tiếng được đo và đối chiếu từ MP4. Chưa nghe trực tiếp, xem liên tục toàn bộ hoặc thử thiết bị chiếu tại tiệc.

[Các khung từ bản xuất 1–42](../previews/slideshow-final-1.jpg) · [43–84](../previews/slideshow-final-2.jpg) · [85–126](../previews/slideshow-final-3.jpg) · [Điểm đổi bài](../previews/slideshow-song-boundaries.jpg)

## Bản giao V005

- MP4 có hình H.264 BT.709 YUV420p 1920 × 1080 ở 50 fps, 137.646 khung, và AAC stereo 48 kHz. Xác nhận cả hai track dài 2.752,92 giây, 13 mốc chapter và timeline PTS/DTS liên tục. Đã giải mã hết hình và tiếng.
- Đã xem một khung giữa mỗi cảnh, toàn bộ 28 cụm chữ, 24 mẫu chữ vào/giữ/ra và 36 mẫu quanh các lần đổi bài. Đọc từ khung Full HD hai tên và hai ngày ở đoạn mở, đoạn Song Hỷ và khung cuối. Xác nhận ảnh hai bé có ở chương 1 và chương 8.
- Đo nhạc −18,04 LUFS, đỉnh thực −6,07 dBTP. Đối chiếu AAC với WAV ở ba đoạn trong mỗi bài, tương quan thấp nhất 0,99740. Phép dò khoảng dưới −48 dBFS từ 0,7 giây chỉ báo đoạn cuối phim. Mỗi bài dùng đúng hash của tệp nguồn đã đối chiếu.
- Đã lấy mẫu chuyển động đoạn mở trên file thử ở hai vùng, với bước khung 20 ms. Bước dịch phân vị 95 là 0,475 pixel ở ảnh hai bé và 0,075 pixel ở ảnh cưới. Báo cáo này đo các vùng lấy mẫu, chưa thay cho việc xem nghe liên tục và chạy thiết bị chiếu tại tiệc.

[Tất cả cụm chữ, phần 1](../previews/v005/encoded-text-01.jpg) · [Phần 2](../previews/v005/encoded-text-02.jpg) · [Chữ vào, giữ, ra](../previews/v005/encoded-text-motion.jpg) · [Khung cuối](../previews/v005/encoded-last-frame.jpg) · [Bằng chứng QA](../../../docs/production/evidence/2026-11-25-wedding-slideshow-v005.json)
