# Quyết định dựng

- 7 clip đều 1920×1080, 24 fps, dài xấp xỉ 9,96 giây; tổng lượng nguồn khoảng 70 giây. Đã xem contact sheet 5 thời điểm mỗi clip.
- Toàn bộ tiếng gốc bị loại bằng `-an` khi tạo montage; composition cũng dùng video muted. File giao sẽ chỉ mux soundtrack mới, không map bất kỳ audio stream gốc nào.
- Giữ cảnh thực tế có sẵn, không tạo thêm ảnh hoặc thay nhận diện. Typography dùng Manrope từ google/fonts, giấy phép OFL lưu cùng font.
- Đã chuẩn bị composition Remotion và môi trường 4.0.540, nhưng bước khởi chạy browser từ Node bị hệ điều hành từ chối `spawn EPERM`. Không nâng quyền. Bản xuất thật chuyển sang renderer FFmpeg native có typography/gradient/timing xác định, lưu trong src/render_ffmpeg.py. Bản Remotion được giữ làm phương án tham khảo, chưa xác minh render hoạt động.
- Bản native dùng Segoe UI Regular/Bold từ hệ điều hành để đảm bảo độ rõ của chữ nhỏ và dấu tiếng Việt. Manrope cùng OFL vẫn được giữ cho composition tham khảo. Không phát hành lại file font hệ điều hành cùng bản giao.
- Source footage chỉ copy sang public để renderer truy cập; không đổi file gốc.
- Đã tìm SFX trên Mixkit, Pixabay và các thư viện cinematic; một số host từ chối tải bằng client hiện có. Asset sử dụng thật là Kenney Interface Sounds qua bản mirror GitHub có manifest CC0, kiểm tra trang tác giả chính chủ xác nhận CC0.
- Whoosh, riser, impact và text accent là lớp sound design tạo bằng code với seed cố định, không lấy tiếng phim gốc. Có source và timeline để chỉnh lại.
- Nhạc người dùng cung cấp dài 466 giây; chọn đoạn bắt đầu 19,71 giây trên lưới nhịp được đo từ waveform. Việc dùng file được cung cấp không xác minh thay giấy phép phát hành của bản nhạc.
- Môi trường này không hỗ trợ nghe trực tiếp audio trong mô hình; QA âm thanh dùng waveform, transient alignment và loudness/true-peak. Không ghi nhận là đã nghe duyệt bằng tai.

## V002 — theo phản hồi người dùng

- Dựng lại phần hình bằng Remotion 4.0.540 / React 19.2.0. Composition thật ở `src/v002-film.tsx`, entry chuẩn ở `src/v002-entry.tsx`; font Manrope từ Google Fonts, giữ giấy phép OFL.
- Các chuyển động đều tính từ frame: spring theo từng từ, rotateX, scale, blur reveal, chữ viền, panel kiến thức, montage chữ lớn và graphic wipe. Đã kiểm tra 11 frame từ chính renderer trước khi xuất 975 frame.
- Headless Chrome của Remotion không khởi chạy được trong quyền hiện tại (Windows pipe/Mojo IPC bị từ chối). Không sửa thiết lập bảo mật hoặc nâng quyền. Đường xuất chạy được là Remotion Player trong Chrome đang có, seek chính xác từng frame, chờ font/ảnh rồi rasterize DOM bằng html-to-image; POST JPEG chỉ tới server 127.0.0.1 trên máy này. FFmpeg chỉ encode và ghép soundtrack sau khi hình đã được Remotion dựng.
- Footage đã cắt giữ trong montage không tiếng, trích 975 frame để tránh phụ thuộc video decode của headless browser. Không lấy audio gốc vào composition hoặc MP4.
- SFX v002 được tạo mới, seed 260203: impact trầm, slam cho chữ, whip stereo, riser, tick. Tổng 64 cue; v002 không dùng lại các file click Kenney của v001. Nhạc cùng nguồn người dùng nhưng lấy đoạn đầy hơn từ 38,07 giây.
- Bản v001 và các file bàn giao cũ được giữ nguyên. Bản v002 có tên riêng, kèm soundtrack WAV và poster.

## V003 ? 03/11/2026

- Ng??i d?ng ?? giao tri?n khai ph??ng ?n ph?i h?p repo, nh?n m?nh text FX.
- Gi? code v001/v002; v003 n?m trong src/v003, public/v003, working/v003, previews/v003. Metadata tr??c s?a l?u ? working/v003/prior.
- D?ng package ?? kh?a: GSAP 3.15.0, @remotion/gsap/fonts/media 4.0.540. Kh?ng s?a c?y source vendored.
- Browser headless ?i k?m Remotion ?? render smoke th?nh c?ng trong m?i tr??ng hi?n t?i; kh?ng c?n ???ng rasterize DOM v002.
- FFmpeg/ffprobe n7.1 c? s?n trong node_modules/@remotion/compositor-win32-x64-msvc; kh?ng ph? thu?c ???ng d?n C:/Users/Hero.
- SHA-256 8 nguy?n li?u ???c ch?n ?? ???c ??i chi?u; source gi? nguy?n.

### V003 ? ch?t b?n giao

- ?? xu?t tr?c ti?p t? composition Remotion + GSAP, kh?ng d?ng rasterize DOM c?a v002.
- Ch?n PNG v? BT.709 limited range cho b?n cu?i sau khi QA ph?t hi?n encode m?c ??nh full range. C?c candidate c? l?u trong working/v003 ?? ??i chi?u; b?n cu?i ???c render l?i t? composition.
- Ch? vi?n chuy?n sang fill r?i bi?n m?t, ?? d?u ti?ng Vi?t kh?ng c? n?t d?; nh?n m? ph?ng ???c ??a cao h?n.
- K?t th??ng hi?u b?t ??u frame 860, gi? kho?ng 4,79 gi?y g?m animation v?o v? fade cu?i. Timeline v003 l? ngu?n chung cho th?i gian shot/chuy?n c?nh.
- ?? giao v003 ri?ng, k?m WAV, poster, contact sheet v? delivery-v003.md; ch?a ph?t h?nh ra ngo?i.

## V004 ? s?a l?i d?u ???c ng??i d?ng ch? ra

- ?? t?i hi?n l?i v?i c?ng font Manrope: clipPath inset(0) tr?n span c?t ph?n glyph v??t line box. Font c? c? glyph; padding cha kh?ng c?u clip c?a span.
- B? clipPath v? overflow c?c b? tr?n ch?, chuy?n animation theo t? NFC.
- Be Vietnam Pro 400/500/600/700 c? ??y ?? glyph ???c s? d?ng; source/sha/license l?u c?ng v004.
- Th?m stroke sau fill, shadow nh?, d?ng m?u xanh n??c bi?n #168fe5.
- Hai l?p outline/fill d?ng c?ng c?u tr?c kho?ng c?ch; tr?nh b?ng d?u b? l?ch do word spacing kh?c nhau.
- Gi? nguy?n media/timeline/soundtrack, code v004 ri?ng; v003 v? t?t c? b?n giao c? ???c hash tr??c s?a.
- Reference GSAP masks v? Mixkit kinetic ?? ???c xem tr?c tuy?n; kh?ng nh?n MOGRT l? template ch?y ???c trong Remotion.
