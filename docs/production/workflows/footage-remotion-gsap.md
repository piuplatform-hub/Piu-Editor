# Dựng TVC từ footage bằng Remotion + GSAP + FFmpeg

Nguồn thực tế: [TVC Yên Thành, 03/11/2026](../cases/2026-11-03-yen-thanh-tvc.md). Phạm vi đã dùng: video ngang Full HD, 24 fps, footage có sẵn, typography 2D, nhạc và SFX. Với tỷ lệ, FPS, font hoặc engine khác, kiểm tra lại phần bị ảnh hưởng.

## 1. Phân công công cụ

| Repo | Việc đảm nhiệm |
|---|---|
| [Remotion](../../../repos/09-remotion/AGENTS.md) | Composition, lớp hình/chữ, Sequence và thời điểm theo frame |
| [Remotion Skills](../../../repos/01-remotion-skills/AGENTS.md) | Hướng dẫn cấu trúc, media/font và render |
| [GSAP](../../../repos/05-gsap/AGENTS.md) | Phối chuyển động nhiều lớp, stagger, easing; CustomEase và DrawSVG khi cần |
| [GSAP Skills](../../../repos/02-gsap-skills/AGENTS.md) | Timeline, bố trí chuỗi animation và vòng đời React |
| [FFmpeg](../../../repos/18-ffmpeg/AGENTS.md) | Cắt/chuẩn hóa clip, audio mix/master, encode và kiểm tra media |

Đọc guide trước khi dùng. Source trong `repos/` là tài liệu và mã tham khảo. Package chạy thật nằm trong project và có lockfile. Bộ đã chạy trong ca nguồn: Remotion và các package `@remotion/*` 4.0.540, GSAP 3.15.0, React 19.2.0, FFmpeg/ffprobe n7.1 đi kèm dependency trên Windows. Đây là bộ phiên bản ghi nhận cho ca nguồn; xác minh lại khi dùng ở môi trường khác.

## 2. Hiểu nguyên liệu và câu chuyện

1. Tiếp tục đúng project; đọc brief, trạng thái, decisions và asset selection.
2. Chạy inventory có hash, xem contact sheet/clip và kiểm tra ffprobe. Đọc nội dung từ file thật.
3. Viết mạch kể ngắn trước khi dựng: mở → chứng minh → tăng nhịp → kết thương hiệu. Chọn một thông điệp chính mỗi cảnh.
4. Chọn vị trí chữ theo chủ thể, vùng trống và hướng camera. Phân biệt cảnh cần chữ với cảnh nên để hình tự kể.
5. Giữ nguyên bản nguồn; proxy và bản cắt ở khu vực dẫn xuất của project.

## 3. Kiểm tra đường render sớm

Chạy một still đơn giản bằng browser đi kèm Remotion, rồi một đoạn ngắn có font, footage và audio. Xác nhận file thật trước khi dựng toàn phim. Khi lỗi môi trường xuất hiện, ghi lỗi cùng phiên bản và kiểm tra lại ở môi trường hiện tại.

Trong ca Yên Thành, v001/v002 từng ghi nhận lỗi khởi chạy browser; đến lượt dựng v003, browser đi kèm render được. Vì vậy ghi chú lỗi cũ chỉ là đầu mối để kiểm tra.

Nếu `doctor` chưa thấy FFmpeg trong PATH, kiểm tra binary thuộc dependency project trước khi kết luận thiếu. Binary đi kèm có thể lược bớt filter, muxer hoặc encoder; thử đúng thao tác cần dùng. Xem [bài học runtime](../cases/2026-11-03-yen-thanh-tvc.md#bài-học-kỹ-thuật).

## 4. Một chuẩn thời gian

- Chốt FPS, resolution và tổng frame theo brief.
- Lưu các shot bằng `start`, `end`, `sourceStart`; quy định `end` không bao gồm frame cuối. Tính thời lượng bằng `(end - start) / fps`.
- Dùng cùng dữ liệu để dựng hình và căn các điểm nhấn. Khi copy mốc sang code riêng, kiểm tra lại sự nhất quán; bản Yên Thành còn vài mốc montage được viết trực tiếp, cần rà nếu đổi timeline.
- Với GSAP trong Remotion, dùng timeline được điều khiển theo frame qua adapter phù hợp. Không để ticker/autoplay độc lập chi phối bản xuất.
- Bảo đảm font, ảnh và media tải xong trước khi capture. Dùng seed cho thành phần ngẫu nhiên.

## 5. Xây hệ chữ và chuyển động

Tạo vài thành phần có vai trò rõ: tiêu đề chính, nhãn nhỏ, outline-to-fill, chữ montage và chữ kết. Cho từng cảnh chọn kiểu phù hợp, đồng thời giữ một hệ font/màu/khoảng cách thống nhất.

V004 sử dụng:

- `TextFx`: animate nguyên từ đã chuẩn hóa NFC bằng translate, opacity và rotation nhỏ.
- `FillFx`: outline và fill dùng cùng cấu trúc span/khoảng cách; fill hiện theo từ rồi outline biến mất.
- `Label`: nhãn nhỏ và nét nhấn vào lệch nhịp.
- `Road`: SVG path vẽ dần bằng DrawSVG.
- `RoadWipe`: lớp đồ họa che và mở sang cảnh kế tiếp.

Đọc [quy tắc dấu tiếng Việt](../quality/vietnamese-text.md) trước khi áp dụng mask, font hoặc stroke. Cỡ chữ, line-height và thời gian animation trong project mẫu là điểm khởi đầu để thử.

Làm một vài style frame, sau đó preview chuyển động có tiếng trước khi mở rộng. Giữ chữ đủ lâu để đọc sau khi vào, tạo khoảng hình sạch, và căn chữ với điểm nhấn âm thanh có chủ đích.

## 6. Âm thanh là một phần của bản xuất

- Chọn đúng asset nhạc trong manifest; giữ đường dẫn và thông tin nguồn.
- Loại hoặc giữ audio footage theo brief, bằng stream map/muted rõ ràng. Kiểm tra các clip dẫn xuất và MP4 cuối.
- Phối nhạc, tiếng chuyển động, nhấn chữ và impact theo timeline. Số lượng cue không chứng minh độ hay.
- Mix thành master WAV rồi dùng master đó trong composition/mux. Đo loudness và true peak sau encode AAC.
- Nghe bản MP4 khi có khả năng nghe; nếu chưa nghe được, ghi rõ. Tương quan waveform với master xác nhận đường audio, chưa đánh giá cảm giác mix.

## 7. Render, kiểm tra và giao

1. Render các frame có chữ nhiều dấu và các biên chuyển cảnh.
2. Kiểm tra animation ở giai đoạn vào/giữ/ra, seek không tuần tự; với lỗi chữ, so thêm reference không animate.
3. Xuất tên phiên bản mới; từ chối ghi đè bản giao có sẵn theo mặc định.
4. Chọn pixel format và color space rõ ràng. Ca nguồn dùng PNG làm frame trung gian, H.264 `yuv420p`, BT.709 limited, AAC stereo 48 kHz.
5. Đọc thông số từ MP4, decode toàn bộ, trích frame để xem lại và đo audio sau AAC. Phân biệt độ dài video với độ dài container do biên audio.
6. Đối chiếu hash nguyên liệu và các bản cũ cần giữ. Ghi delivery, lệnh tái tạo, kết quả QA và giới hạn.
7. Ghi [tổng kết vòng dựng](../../../templates/project/notes/retrospective.md), cập nhật hồ sơ và bài học đã có bằng chứng.

## Điểm vào mã đã chạy

- [Composition v004](../../../projects/tvc-driving-premium/src/v004/Film.tsx)
- [Timeline](../../../projects/tvc-driving-premium/src/v004/timeline.json)
- [Chuẩn bị media/font/audio](../../../projects/tvc-driving-premium/src/v004/prepare.py)
- [Render](../../../projects/tvc-driving-premium/src/v004/render.cjs)
- [QA MP4](../../../projects/tvc-driving-premium/src/v004/qa.py)
- [Hướng tái tạo riêng của project](../../../projects/tvc-driving-premium/notes/render-v004.md)

Các script này có đường dẫn, nội dung, clip và tên output của Yên Thành. Khi tái sử dụng, lập project mới, thay nguồn theo manifest và parameter hóa phần cần dùng; chưa coi đây là template độc lập có thể chạy với mọi video.
