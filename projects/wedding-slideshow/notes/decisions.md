# Quyết định của dự án

## Hình

- Chọn 77 ảnh album và 99 ảnh trong thư mục con sau khi khảo sát các nhóm ảnh. Các ảnh dùng trên timeline được ghi trong `assets.json` cùng SHA-256. Lưu bản sao trong `Source/inbox/wedding-slideshow`.
- Năm kiểu bố cục gồm ảnh ngang tràn khung và các biến thể hai, ba ảnh dọc. Các ô ảnh chiếm ít nhất 95% diện tích nền bố cục trước chuyển động. Dùng viền ngà hoặc đỏ rượu mảnh, căn crop lên phần mặt và bờ vai ở ô rộng.
- Có 322 lượt đặt ảnh trong 126 cảnh. Khi một ảnh quay lại, lần xuất hiện kế tiếp đổi bố cục hoặc hướng chuyển động. Dùng tan hình và lau mép mềm, giữ phần cuối mỗi cảnh ổn định để khách dễ nhìn khi ăn tiệc.

## Nhạc

- Dùng 10 bản MP3 có sẵn, đối chiếu theo ảnh thứ tự. Mục “Đến Khi Nào” dùng đúng file “Đến Khi Nào (Drill)” hiện có. Bốn mục chưa có tệp là “Lỡ thương nhau”, “Gói con tim làm quà”, “Ngày chung đôi” và “My love”.
- Cân mức về khoảng −18 LUFS trước khi chồng 1,12 giây ở biên bài. Bản ghép thô lộ khoảng yên tới 8,76 giây. Đã rút 34,84 giây âm lượng rất thấp ở đầu/cuối các tệp theo ngưỡng −49 dBFS, chừa khoảng đệm 0,24 giây. Bản WAV đã chỉnh không có khoảng dưới −48 dBFS kéo dài từ 0,7 giây theo phép đo.
- Chia lại độ dài các cảnh theo bản nhạc đã chỉnh. Thứ tự các ảnh và bài hát dựa trên [timeline](../src/timeline.json).

## Tái tạo

Máy dựng dùng Python 3.10, các phiên bản trong `requirements-render.txt` và FFmpeg n7.1 có sẵn của project mở màn. Có thể trỏ `PIU_WEDDING_FFMPEG_DIR` đến nơi chứa binary tương thích.

1. `python -B -X utf8 src/media.py audio "D:\Edit Video Cuoi"` tạo lại WAV.
2. `python -B -X utf8 src/media.py photos "D:\Edit Video Cuoi"` đối chiếu và chuẩn bị ảnh theo timeline đã lưu.
3. `python -B -X utf8 src/render.py preview` xuất bản thử hình. `python -B -X utf8 src/render.py final` xuất đầy đủ vào vị trí V001 còn trống.
4. `python -B -X utf8 src/qa.py` giải mã và kiểm tra file thật.

## Vòng thử V002

Tham khảo cách xếp khung vòm, hoa màu nước, nét mờ và vệt sáng của mẫu người dùng gửi. Đặt chúng so le với các cảnh ảnh tràn màn và giữ chữ mở “Từ hôm nay”. Chọn 22 tấm từ bộ ảnh mới, với cảnh Song Hỷ bắt đầu ở 52,36 giây. [Hồ sơ và lệnh của bản thử](preview-v002.md)

## Bản chiếu tiệc V005

- 54 ảnh riêng biệt theo catalog đã đối chiếu hash, 261 cảnh và 28 cụm chữ. Ảnh hai bé ở đầu và trong “Photograph”. Tránh dùng lại cùng ảnh ngay cảnh kế tiếp. Một số chân dung được crop cận khi lên toàn khung.
- Tái sử dụng font, họa tiết và chuyển động ở các vòng demo. Dùng Remotion để tạo các lớp chữ, GSAP tính vị trí và độ mờ theo frame, OpenCV ghép ảnh ở tọa độ phần lẻ và FFmpeg xuất bản giao cùng nhạc. Mỗi chương có file hình và hash để có thể tiếp tục sau gián đoạn.
- Nhạc dùng đúng 13 MP3 trong thư mục nguồn sau khi đối chiếu. Giữ đoạn nhỏ có chủ đích trong bài và xử lý đoạn gần im ở hai mép. [Kịch bản và lệnh tái tạo](kich-ban-v005.md)
