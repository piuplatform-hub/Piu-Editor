# Từ hôm nay

Phim mở màn dành cho khách mời trong tiệc cưới. Bộ ảnh studio trắng và bàn tiệc sáng tạo cảm giác gần gũi. Sắc đỏ Song Hỷ xuất hiện khi nhạc dâng, rồi phim trở về tông ngà để hiện tên hai bạn và lời cảm ơn.

[Bảng bốn khung minh họa bằng ảnh thật](previews/storyboard-v001.png)

## Mạch phim dự kiến

| Thời gian | Hình và chuyển động |
|---|---|
| 00:00–00:08 | Mở bằng ảnh ngang `PAD_4549`. Chữ “Từ hôm nay” hiện ở vùng sáng bên trái, ảnh tiến nhẹ vào hai bạn. |
| 00:08–00:28 | Đặt hai chân dung cạnh nhau như trang album. Chuyển sang ảnh dìu tay, xoay váy và khoảnh khắc dưới khăn voan. |
| 00:28–00:52 | Chuyển nhịp theo loạt ảnh chạm tay, hôn tay, nâng ly và cười. Đổi cỡ ảnh từ toàn thân sang cận mặt để kể bằng biểu cảm. |
| 00:52–01:12 | Mở phông đỏ như rèm sân khấu, hiện “Ngày chung đôi”. Xen ảnh toàn thân với ảnh cận quạt, trang phục và ánh mắt hai bạn. |
| 01:12–01:20 | Giữ ảnh cận `PAD_4238` cạnh tên, ngày cưới và lời “Cảm ơn đã đến chung vui cùng chúng mình”. Hạ nhạc theo câu để chuyển sang phần sân khấu. |

[Danh sách ảnh và cách đặt từng cảnh](notes/shot-list.md)

## Hình, chữ và tiếng

- Dùng trắng ngà, nâu ấm và đỏ rượu vang. Giữ bố cục dọc cho ảnh toàn thân để thấy được váy và trang phục. Chỉ crop cận khi ảnh có khoảng trống phù hợp.
- Cormorant Garamond cho tiêu đề và tên, Be Vietnam Pro cho lời cảm ơn và ngày. Chữ hiện theo cụm bằng dịch chuyển ngắn và đổi opacity. Kiểm tra dấu ở lúc chữ vào, giữ và ra.
- Đề xuất một đoạn từ “Ngày Đầu Tiên” của Đức Phúc, bài số 1 trong ảnh danh sách nhạc. Mở nhẹ ở phần đầu bài, thử vào chương Song Hỷ quanh vùng nhạc dày hơn ở 52 giây, rồi chọn điểm kết trọn câu khi dựng preview. Hiện dự kiến để ảnh, chữ và nhạc dẫn phim.
- Dự kiến một lần chiếu trước phần mời hai bạn bước vào. Preset đề xuất là MP4 H.264/AAC, màn ngang 16:9, 1920 × 1080 ở 30 fps, khoảng 80 giây. Tên hiển thị, ngày cưới và thời điểm chuyển sang MC hoặc nhạc vào lễ sẽ điền theo thông tin của hai bạn.

## Mẫu tham khảo

- Cách đặt chữ serif cạnh ảnh và cho mỗi cụm chữ xuất hiện theo nhịp từ demo ảnh cưới của Mộng Mer. [Mộng Mer](https://mongmer.com/video-cuoi)
- Cách trình bày ảnh và lời ngắn như một cuốn photobook mở màn tiệc. [Wedding Day của With Produce](https://with-produce.co.jp/photo-movie/opening-movie)

## Chuẩn bị dựng

Nguồn gốc ở `D:\Edit Video Cuoi`. Đã xem 77 ảnh cưới, trong đó có 76 ảnh dọc, và kiểm tra thông tin kỹ thuật của 10 MP3. Năm ảnh trong bảng phân cảnh và bài nhạc đề xuất có bản sao cục bộ đã ghi hash để dùng lại. Remotion sẽ phụ trách bố cục, chữ và nhịp chuyển theo frame. FFmpeg dùng để kiểm tra và xử lý đường âm thanh cũng như xác minh MP4 sau xuất.
