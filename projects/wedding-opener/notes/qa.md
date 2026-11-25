# Kiểm tra chất lượng

## Bảng phân cảnh V001 · 25/11/2026

- Đã mở ảnh PNG 1600 × 1120 và xem cả bốn khung 16:9. Tiêu đề, “Ngày chung đôi” và lời cảm ơn hiển thị đủ dấu. Dời ảnh mở sang phải để hai gương mặt nằm ngoài lớp sáng hỗ trợ chữ.
- Năm ảnh được chọn cho storyboard và một MP3 đề xuất có SHA-256 khớp bản gốc. Kiểm tra ffprobe trên 10 MP3, trong đó “Ngày Đầu Tiên” dài 208,97 giây, stereo 48 kHz.
- Chạy `python -X utf8 scripts/studio.py validate --sources` đạt 18 công cụ, 5 project, 0 lỗi, 0 cảnh báo. Thêm `--local` báo 48 mục nguồn và đầu ra thiếu của `tvc-driving-premium`. Kiểm tra riêng sáu file của `wedding-opener` đạt.
- Phạm vi QA là hình tĩnh và thông tin file audio. Cần nghe nhạc, xem chuyển cảnh, kiểm tra chữ ở các pha animation và xác minh MP4 sau khi dựng.

[Xem storyboard V001](../previews/storyboard-v001.png)

## MP4 V001 · 25/11/2026

- Remotion 4.0.540 xuất đủ 2.299 khung phần hình chính và 293 khung thẻ kết. FFmpeg n7.1 ghép hai phần hình với nhạc, tạo MP4 31.351.907 byte. `npm run render` và `npm run qa` đều thoát với mã 0.
- FFprobe xác minh 1920 × 1080, 30 fps, 2.592 khung H.264, BT.709, AAC stereo 48 kHz. Cả hai track dài 86,4 giây. Giải mã hết hai track thành công. Các mốc thời gian hình cách nhau 1/30 giây và 4.051 gói AAC liền nhau theo timestamp.
- Xem 32 khung đại diện lấy từ MP4 cùng 54 mẫu quanh đầu, cuối và 16 điểm chuyển cảnh. Kiểm tra ảnh cận, bố cục ngang, dấu và dòng chữ trong “Từ hôm nay”, “Ngày chung đôi” và “Cảm ơn đã đến chung vui cùng chúng mình”. Cảnh Song Hỷ vào ở 52,63 giây. Phần tan hình sang thẻ cảm ơn từ 76,63 giây hiện đủ trên các khung lấy mẫu sau điểm nối.
- Đo nhạc ở −15,54 LUFS, đỉnh thực −6,04 dBTP. Tương quan với WAV ghép gốc lớn hơn 0,99985 tại bốn cửa sổ lấy mẫu gồm đoạn hạ nhạc. Mẫu sau mốc 86,1 giây đạt ngưỡng yên lặng của QA.
- Đối chiếu SHA-256 của 20 ảnh và một MP3 đã chọn với bản gốc người dùng cung cấp. Cả 21 bản sao đều khớp.
- Đánh giá hình dựa trên khung trích từ bản giao. Tiếng được giải mã và đo trên máy. Chưa nghe bằng tai, xem chuyển động liên tục hoặc thử trên thiết bị chiếu tiệc.

[Bảng 32 khung từ bản xuất](../previews/v001/encoded-contact.jpg) · [Biên chuyển cảnh 1–8](../previews/v001/cut-boundaries-01.jpg) · [Biên chuyển cảnh 9–16](../previews/v001/cut-boundaries-02.jpg)
