# Từ hôm nay — Bản thử V002

[Mở MP4 thử](../previews/v002/tu-hom-nay-v002-preview.mp4) · 64,72 giây · 1920 × 1080 · 25 fps · H.264 và AAC stereo

Nguồn tham chiếu là “Romantik Love Story” trong `D:\Edit Video Cuoi\wedding folder`. Đã xem ba trang của `Help.pdf`, kiểm tra thông tin cảnh trong `wedding.aep` và xem mẫu các tệp hoa, lá, bokeh và vệt sáng. Bản thử dựng các bố cục trong Piu Editor, ghép tám lớp hiệu ứng từ thư mục mẫu. Máy dựng chưa có runtime After Effects được xác nhận để chạy `wedding.aep`.

| Mốc | Hình và chuyển cảnh |
|---:|---|
| 00:00 | Ảnh ngang tràn màn, chữ “Từ hôm nay” hiện nhẹ. |
| 00:07 | Mở vòm và ghép ảnh kỷ niệm, điểm hoa và lá màu nước. |
| 00:12 | Vệt sáng ấm dẫn sang bộ chân dung xếp lệch. |
| 00:19–00:45 | Ảnh khăn voan, nâng ly, dáng váy và ảnh bàn tiệc. |
| 00:46 | Vòm hoa cạnh ảnh hai bạn. |
| 00:52 | Sang bộ ảnh Song Hỷ với vệt sáng đỏ, viền vàng mảnh và bokeh. |
| 00:59 | Về bộ ảnh sáng và hạ nhạc cuối bản thử. |

Đã giải mã 1.618 khung hình và track AAC từ MP4. Đã xem khung của 10 cảnh và 27 khung quanh 9 điểm chuyển. Kiểm tra dấu ở chữ mở, crop mặt, bố cục và mức nhạc −19,91 LUFS, đỉnh thực −10,26 dBTP. Chưa nghe trực tiếp hoặc thử trên thiết bị chiếu. Bản chiếu tiệc 33 phút V001 vẫn có thể mở từ [file giao trước](../../../output/wedding-slideshow/tu-hom-nay-slideshow-v001.mp4).

Từ thư mục dự án, `python -B -X utf8 src/v002/prepare.py "D:\Edit Video Cuoi"` đối chiếu nguồn theo [catalog đã khóa](../src/v002/curated.json). `python -B -X utf8 src/v002/preview.py stills` dựng khung thử và `python -B -X utf8 src/v002/preview.py render` xuất rồi kiểm tra MP4. Nhạc bản thử lấy từ WAV của V001 đã xác nhận hash. [Timeline thử](../src/v002/preview-plan.json) · [Khung kiểm tra chuyển cảnh](../previews/v002/preview-transitions.jpg)

## Sửa chuyển động theo phản hồi

Người dùng thấy ảnh rung trong lúc phát. MP4 25 fps có đủ 1.618 khung và các mốc PTS cách đều nhau. Lỗi xác nhận được nằm ở cách đặt vị trí các lớp ảnh. Mỗi khung làm tròn vị trí sang pixel nguyên, nên ảnh đứng yên trong một số khung rồi dịch cả một pixel.

Đã dùng vị trí theo phần lẻ của pixel cho ảnh, hoa lá và chữ. Làm mịn biên khung vòm và nội suy lại thời gian của lớp vệt sáng. Dựng lại ở 50 fps theo các mốc cảnh cũ. [Mở MP4 50 fps](../previews/v002/muot/tu-hom-nay-v002-muot.mp4)

So hai file theo cùng bước 40 ms bằng tương quan pha trong vùng ảnh ở cảnh Chân dung và Khoảnh khắc bên nhau. Bản 25 fps có 24 và 16 lần dịch trên 0,5 pixel ở hai vùng đo. Bản 50 fps có 0 lần ở cả hai vùng. Giải mã hết 3.236 khung và xác nhận các mốc PTS cách nhau 20 ms. Toàn bộ 3.035 gói AAC có dữ liệu và mốc thời gian giống bản thử trước. Cảm nhận khi phát trên thiết bị của người dùng còn cần kiểm tra.

Lệnh tái tạo là `python -B -X utf8 src/v002/preview.py render --smooth`. [Bằng chứng đo](../../../docs/production/evidence/2026-11-25-wedding-slideshow-v002-motion.json)
