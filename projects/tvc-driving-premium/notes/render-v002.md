# Tái tạo bản Remotion v002

Chạy trong `projects/tvc-driving-premium`. Dependency đã khóa trong `package-lock.json`.

1. `npm run prepare:v002`: trích các frame nền từ montage `public/video/edit-base.mp4`, tạo bộ SFX và master nhạc. Chỉ cần chạy lại khi sửa nền hoặc tiếng. Montage được tạo bằng pipeline chuẩn bị v001, không chứa audio gốc.
2. `npm run build:v002`: bundle giao diện Remotion Player vào `working/v002-ui`.
3. `npm run preview:v002`: mở server chỉ trên `127.0.0.1:8765`. Mở địa chỉ này bằng Chrome; dùng **Lưu khung xem thử** để kiểm tra 11 frame, sau đó **Xuất toàn bộ frame Full HD**. Giữ tab hoạt động và cửa sổ Chrome hiển thị cho đến khi giao diện báo xong 975 frame. Chrome có thể tạm dừng requestAnimationFrame khi cửa sổ bị che hoàn toàn; đưa Chrome ra trước để tiếp tục, không cần xuất lại.
4. `npm run render`: kiểm tra bộ frame hoàn chỉnh, encode H.264 và mux soundtrack mới, copy WAV/poster, decode toàn bộ và kiểm tra ffprobe/loudness/hash nguồn. Lệnh dùng `-n` để không ghi đè file MP4 đã có; lần sửa tiếp theo cần tăng số phiên bản trong script trước khi xuất.
5. `python src/encode_v002.py --qa-only`: kiểm tra lại file v002 có sẵn, không xuất lại.

Hình xuất thật là composition `PremiumFilmV2` của Remotion, 1920×1080, 24 fps, 975 frame. Browser frame capture dùng html-to-image 1.11.13, chờ tải font và ảnh; JPEG quality 0.985, không thu màn hình hoặc phụ thuộc kích thước cửa sổ.

`npm run studio` mở composition v002 bằng Remotion Studio. Entry chuẩn cũng có lệnh `npm run render:v002:cli`; đường CLI headless chưa chạy được trên máy này do Windows từ chối IPC của Chrome. Lệnh đó chỉ xuất hình vào working; muốn dùng ở máy khác vẫn cần mux soundtrack v002. Không coi CLI là đường đã được kiểm chứng.

Âm thanh được mix thật bằng FFmpeg từ `public/soundtrack-v002.wav`, không thu tiếng loa/browser. Audio player trên giao diện chỉ dùng nghe riêng; chưa đồng bộ play/pause với Player. Xem MP4 cuối để đánh giá hình và tiếng cùng nhau.

Các file `remotion-file-stdio.cjs`, `remotion-smoke.tsx`, `smoke-render.cjs` và log browser trong working là chẩn đoán lỗi headless, không thuộc pipeline xuất thành công.
