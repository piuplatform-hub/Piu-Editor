# Dựng slideshow ảnh theo danh sách nhạc

Quy trình này đúc kết từ phim mở màn “Từ hôm nay” và bản chiếu tiệc V005. Phim mở màn dùng Remotion để dựng hình. Bản chiếu tiệc dài 45 phút 52,92 giây dùng Remotion cho chữ, GSAP cho chuyển động, PyAV và OpenCV cho khung hình 50 fps, FFmpeg để ghép âm thanh và kiểm tra. [Hồ sơ phim mở màn](../cases/2026-11-25-wedding-opener-v001.md) · [Hồ sơ bản chiếu tiệc](../cases/2026-11-25-wedding-slideshow-v005.md)

## 1. Chốt nguồn và mạch kể

1. Xác nhận mục đích chiếu, thứ tự và phiên bản từng bài, tên và ngày hiển thị. Đọc metadata bằng ffprobe. Ghi rõ nếu tệp nhạc người dùng cung cấp là bản phối khác.
2. Xem bảng ảnh trước khi dựng. Ghi hash và đánh dấu ảnh nào chịu được crop. Ghép ảnh dọc thành cặp hoặc bộ ba. Dùng ảnh ngang tràn màn, khung vòm và cảnh cận để thay nhịp.
3. Lập mạch theo chương nhạc. V005 mở bằng ảnh hai bé rồi nối lại với ảnh cưới ở “Photograph”. Các đoạn khác tránh lặp cùng ảnh ở hai cảnh liền nhau.
4. Viết chữ thành câu ngắn và chừa cảnh chỉ có hình với nhạc. Đặt tên và ngày ở các mốc chính. Lưu câu chữ, ảnh và các mốc trong kịch bản và timeline.

## 2. Ghép nhạc và khóa timeline

- Giải mã đúng track audio khi MP3 có ảnh bìa. Chuẩn hóa stereo 48 kHz, đo loudness và true peak trước khi chỉnh gain.
- Đo khoảng âm lượng thấp ở đầu và cuối tệp, chừa đệm và nối bằng crossfade. V005 dùng 1,12 giây. Đo lại bản ghép để phát hiện khoảng im ngoài ý muốn.
- Tính độ dài hình bằng frame nguyên và độ dài tiếng bằng số mẫu. Ở 50 fps và 48 kHz, mỗi frame tương ứng 960 mẫu. Căn mốc chuyển cảnh quanh điểm nhấn trong nhạc. Khi đổi bài, tính lại mốc ảnh và chữ theo bản mix mới.

## 3. Dựng thử hiệu ứng và chữ

- Làm một đoạn ngắn có chữ tiếng Việt, ảnh cận, ảnh toàn thân và một điểm chuyển. Xem MP4 để kiểm tra dấu, đường viền và khoảng cách quanh mặt. [Kiểm tra chữ tiếng Việt](../quality/vietnamese-text.md)
- Với mẫu After Effects, xem tài liệu và kiểm tra các lớp footage. V002 dựng thử với hoa, lá, bokeh và vệt sáng lấy từ thư mục mẫu trên máy chưa xác nhận có After Effects.
- Cho ảnh và chữ chuyển theo frame với tọa độ phần lẻ của pixel. Khi hình rung, kiểm tra các frame liền nhau. Ở V002, mốc thời gian đều nhưng lớp ảnh nhảy một pixel do làm tròn tọa độ. [Đo trước và sau](../evidence/2026-11-25-wedding-slideshow-v002-motion.json)
- Khi kết xuất nhiều lớp chữ bằng Remotion, truyền ID chữ vào bước chọn composition để lấy đúng props. V005 lấy mẫu đường cong GSAP ở 50 fps rồi ghép các lớp chữ lên timeline ảnh. [Mã dựng lớp chữ](../../../projects/wedding-slideshow/src/v005/lettering.cjs)

## 4. Xuất theo chương và kiểm tra bản giao

1. Xuất từng chương hình với cùng codec, kích thước, FPS và time base. Dùng khung cuối chương trước để dựng chuyển cảnh đầu chương sau.
2. Kiểm tra số frame từng chương. Lưu hash đoạn hình và chữ ký của timeline, đầu vào và renderer để khôi phục bản xuất gián đoạn.
3. Thử ghép vài chương với WAV trước khi ghép cả phim. V005 dùng H.264, AAC và chapter theo bài hát. Sau ghép, kiểm tra duration, timestamp liên tục, thứ tự bài, giải mã toàn file và đo âm lượng.
4. Xem khung trích tại các cảnh, các pha chữ vào/giữ/ra và quanh điểm đổi bài. Kiểm tra tên, ngày và ảnh quan trọng từ MP4. Ghi phạm vi xem/nghe và phản hồi người dùng.

Lưu MP4, preview, kết quả đo và bản sao nguồn trên máy. Git lưu code, phiên bản dependency và tóm tắt QA. [Hướng dẫn chạy lại V005](../../../projects/wedding-slideshow/notes/tai-tao-v005.md) · [Quản lý Git](../../GIT.md)
