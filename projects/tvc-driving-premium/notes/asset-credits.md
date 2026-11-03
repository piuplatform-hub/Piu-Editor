# Tài nguyên của bản TVC

## Hình ảnh và nhạc

- 7 video trong `Source/footage/` và bản nhạc trong `Source/music/` do người dùng cung cấp. `assets.json` ghi file đã chọn và SHA256; bản gốc không bị thay đổi.
- Nhạc: `Modern Corporate & Business Background Music - Presentation Music Instrumental - MUSIC4VIDEO.mp3`, chọn đoạn từ 19,71 giây. Chưa có tài liệu giấy phép phát hành kèm file; việc người dùng cung cấp không được mô tả thành giấy phép thương mại đã xác minh.
- Không sử dụng 7 ảnh gốc hoặc tạo ảnh AI mới trong bản dựng này.

## SFX sử dụng thật

- Kenney, Interface Sounds — `click_003.ogg`, dùng làm transient nhẹ cho chữ. [Trang tác giả](https://kenney.nl/assets/interface-sounds) công bố CC0.
- File tải từ [mirror GitHub](https://github.com/GeorgeQLe/assets-sfx-ui), đường dẫn `assets/kenney/interface-sounds/Audio/click_003.ogg`. URL cụ thể và các mẫu đã tải nằm trong `working/sfx-sources.json`; ba mẫu còn lại đã tải để chọn nhưng không được đưa vào mix cuối.
- `design-air.wav`, `design-riser.wav`, `design-impact.wav`, `design-text.wav` được tạo bằng thuật toán trong `src/prepare.py`, seed cố định. Không lấy tiếng từ footage gốc; không dùng sample nhạc/phim của bên thứ ba cho các lớp này.
- Có 45 cue được ghi bằng giây trong `src/sound-events.json`, có thể tái tạo và chỉnh gain/timing.

## Font

- Bản xuất native dùng Segoe UI Regular/Bold từ Windows. Font được rasterize vào video; không kèm file font trong thư mục giao cuối.
- Manrope từ google/fonts được chuẩn bị cho composition Remotion tham khảo; OFL được lưu ở `public/fonts/OFL.txt`. Composition Remotion chưa render được trong phiên này do lỗi spawn EPERM.

## Tái tạo

Từ gốc workspace:

```powershell
python projects/tvc-driving-premium/src/prepare.py all
python projects/tvc-driving-premium/src/render_ffmpeg.py
```

Chỉ tái tạo vào đường dẫn v001 khi muốn thay bản này. Với bản chỉnh sửa, đổi tên output thành v002 trước khi chạy để giữ bản cũ.
