# Quyết định của dự án

Người dùng muốn phim mở màn cho đám cưới, chữ và hiệu ứng đẹp, dùng nguồn trong `D:\Edit Video Cuoi`. Phạm vi hiện tại là khảo sát và đề xuất cách dựng.

- Tựa “Từ hôm nay”, thời lượng 80 giây, màn ngang và vị trí lời cảm ơn là đề xuất dựng. Ảnh dọc được đặt thành cặp hoặc bên cạnh chữ. Ảnh ngang `PAD_4549` dành cho khung mở và sắc đỏ Song Hỷ dành cho đoạn cao trào.
- Chọn “Ngày Đầu Tiên” vì đứng đầu ảnh thứ tự nhạc và file có đoạn đầu nhẹ hơn vùng 50–80 giây theo biên độ đo được. Cần căn câu hát và kiểm tra điểm kết trên preview có tiếng.
- Remotion làm timeline theo frame, có thể dùng `Img` và `staticFile` cho ảnh cục bộ. FFmpeg dùng để chuẩn bị nhạc và kiểm tra đầu ra. Chuyển động ảnh, chữ và các phép lau đơn giản dùng nội suy theo frame của Remotion.
- Phông chữ cho storyboard là Cormorant Garamond và Be Vietnam Pro từ kho Google Fonts. Tên và ngày cưới sẽ dùng nội dung người dùng xác nhận.

## Timeline thực tế của V001

- 20 ảnh từ bộ ảnh gốc được dùng mỗi tấm trong một cảnh, với 17 cảnh. Dùng lưới nhịp ước lượng gần 110 BPM và các điểm nhấn đo được trên bài “Ngày Đầu Tiên” để đặt đường cắt. Tiêu đề Song Hỷ bắt đầu vào 52,63 giây.
- Kéo thời lượng từ khoảng 80 giây lên 86,4 giây để hạ nhạc quanh cuối câu. Thẻ cảm ơn hiện từ 76,63 giây, với đuôi im 0,4 giây để bàn giao nhịp sân khấu.
- Tên và ngày cưới nếu đã chốt được đọc từ `working/wedding-details.json`. Bản mặc định dùng ảnh hai bạn và lời cảm ơn.

## Xuất lại sau khi phiên dựng gián đoạn

- Lần đầu đã lưu timeline và nhạc. Lệnh xuất dừng ở mốc báo 70% của phần hình chính với `write EOF`. Khi đối chiếu trên máy, thư mục làm việc chưa có clip trung gian và thư mục giao chưa có MP4.
- Xuất lại bằng lệnh `npm run render` đã có của project. Bản V001 dùng ảnh và lời cảm ơn ở thẻ kết theo nhánh mặc định vì chưa có tên và ngày cưới trong hồ sơ. Nhạc lấy từ MP3 người dùng đã cấp.
- Đo tiếng từ track AAC đã ghép vào bản xuất. Giữ đoạn hạ nhạc từ 84,15 đến 86,0 giây và phần giữ thẻ cảm ơn đến hết 86,4 giây. [Kết quả kiểm tra](qa.md)
