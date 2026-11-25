# Tổng kết — Từ hôm nay — Slideshow tiệc cưới

Project `wedding-slideshow` giao V001 ngày 25/11/2026.

Áp dụng [cách lưu kinh nghiệm sản xuất](../../../docs/production/README.md). Điền sau một bản giao hoặc vòng phản hồi đáng kể; ghi rõ điều chưa kiểm tra.

## Mục tiêu và kết quả

- Video chiếu lúc khách ăn tiệc. Khung hình dùng cặp ảnh, nhóm ba ảnh hoặc ảnh ngang tràn khung. Chọn 176 ảnh và bố trí thành 126 cảnh. Lần xuất hiện kế tiếp của ảnh lặp đổi bố cục hoặc chuyển động.
- Bản giao là MP4 Full HD 25 fps dài 33 phút 27,48 giây, ghép 10 MP3 theo ảnh danh sách. [File và mốc phát](../../../output/wedding-slideshow/delivery.md)
- Pillow dựng bố cục, OpenCV tạo chuyển động, PyAV 17.0.1 xuất H.264 bằng NVENC và FFmpeg n7.1 ghép, kiểm tra file. [Lệnh tái tạo](decisions.md)

## Phản hồi của người dùng

- Người dùng thấy bản mở màn khá ổn, “còn nhiều khoảng trống quá” và muốn nhiều bài hơn để chiếu lúc ăn tiệc. Slideshow đưa thêm 99 ảnh từ thư mục con và tăng diện tích màn hình có ảnh.
- Bản này phát 10 tệp MP3 có trong nguồn. Ảnh danh sách còn bốn bài chưa có tệp. Chưa có phản hồi của người dùng về bản chiếu tiệc.

## Bài học có thể dùng lại

| Điều kiện / vấn đề | Nguyên nhân đã xác nhận hoặc giả thuyết | Cách xử lý | Kết quả và bằng chứng | Giới hạn |
|---|---|---|---|---|
| Ảnh cưới dọc trên màn ngang có nhiều khoảng trống | Một ảnh dọc đặt riêng cần nhiều nền hai bên | Ghép hai hoặc ba ảnh tương hỗ, giữ viền mảnh và xem từng nhóm trước khi xuất | Ảnh phủ trên 95% diện tích bố cục. Đã xem khung từ 126 cảnh | Mức crop thẩm mỹ còn tùy ảnh và màn chiếu |
| MP3 có biên dài rất nhỏ hoặc im | Đo bản ghép đầu thấy đoạn yên tới 8,76 giây giữa các bài dù đã có chồng tiếng | Đo và rút biên nhỏ của từng tệp trước khi chồng 1,12 giây, căn lại mốc hình | Bản giao qua phép đo 0 khoảng dưới −48 dBFS kéo dài từ 0,7 giây | Chưa nghe thẩm mỹ chuyển nhạc trực tiếp |

## Kiểm tra và bảo toàn

- Đã xem khung trích từ 126 cảnh và 125 điểm chuyển ảnh, gồm chữ đầu/kết. Đã đo track AAC và giải mã toàn bộ MP4. [QA V001](qa.md)
- Đầu vào được đối chiếu SHA-256. Chưa xem liên tục hoặc nghe bằng tai tại địa điểm chiếu.

## Bổ sung cho kho kinh nghiệm

- Ghi lại cách ghép ảnh dọc và đo khoảng yên giữa nhiều MP3, kèm thông số bản dài. [Hồ sơ slideshow V001](../../../docs/production/cases/2026-11-25-wedding-slideshow-v001.md)

## Phản hồi về V001 và bản thử V002

Người dùng nhận xét V001 “hơi đơn điệu”, đã lọc lại ảnh và gửi mẫu After Effects. V002 dùng riêng 22 ảnh trong bộ 55 ảnh đã lọc. Mẫu giúp chọn nhịp chuyển vệt sáng, khung vòm và trang trí màu nước ở một số cảnh. Bản thử 64,72 giây đã giải mã thành công, xem khung ở cả 10 cảnh và các điểm chuyển. Chưa có phản hồi về phong cách V002. [Hồ sơ thử nghiệm](preview-v002.md)

Sau đó người dùng thấy V002 rung và hỏi công cụ nào trong repo phù hợp hơn. Đã đo nguyên nhân là bước dịch 1 pixel trong các lớp ảnh và xuất lại V002 với tọa độ phần lẻ ở 50 fps. Bản V003 thử Remotion + GSAP trên bốn cảnh, xem khung từ MP4, kiểm tra tua ngẫu nhiên và đối chiếu audio. Chờ người dùng xem chuyển động trên thiết bị của họ. [Đo chuyển động V002](preview-v002.md#sửa-chuyển-động-theo-phản-hồi) · [Bản thử V003](preview-v003.md)

## Vòng V004

Người dùng thấy hiệu ứng mượt hơn nhiều và yêu cầu thêm kịch bản, chữ chuyển động tinh tế và hai mốc ngày cưới. Bản thử 47,04 giây có sáu cảnh, trong đó hai cảnh chỉ dùng hình và nhạc. Giữ thẻ ngày ở góc dưới qua hai cảnh cuối. Kiểm tra dáng dấu và số trực tiếp trên các khung MP4 ở hai nền. Chưa có phản hồi về thiết kế chữ của V004. [Kịch bản và QA V004](kich-ban-v004.md)

## Bản chiếu tiệc V005

Người dùng khen bản thử, gửi tên cô dâu chú rể, chốt danh sách 13 bài và nhắc đưa ảnh hai bé vào. Bản 45 phút 52,92 giây dùng 54 ảnh riêng biệt và mạch kể từ ảnh hai bé đến lời cảm ơn. Ảnh hai bé được dùng lại có chủ đích ở “Photograph”.

Chữ được tách theo dòng từ Remotion, áp các mốc chuyển động GSAP ở 50 fps. Để tránh nhầm bộ chữ khi xuất nhiều lớp, truyền ID chữ vào bước chọn composition trước khi chụp từng lớp. Sau khi làm thử phần mở, render hình thành 13 phần và xác minh biên ghép, chapter metadata, hình/tiếng liên tục. Đã xem khung trích và đo audio của cả 13 bài. Chưa thử thiết bị chiếu ở tiệc. [Kịch bản](kich-ban-v005.md) · [QA](qa.md)

Sau khi xem V005, người dùng phản hồi video đẹp và hỏi về tiêu đề YouTube. Đây là phản hồi về bản giao. Chưa xác minh việc tải lên YouTube hay kết quả trên thiết bị tại tiệc. [Quy trình dựng slideshow](../../../docs/production/workflows/photo-slideshow.md)
