# Tái tạo bản chiếu tiệc V005 trên Windows

V005 là bản chiếu tiệc 13 bài của “Từ hôm nay”. Git lưu code, timeline, manifest và hash. Cần khôi phục nguyên liệu trên máy để xuất lại MP4. [Kịch bản và mốc nhạc](kich-ban-v005.md) · [Kết quả QA](qa.md)

## Môi trường và đầu vào

- Dùng Python 3.10 và Node.js 24 như máy dựng. `npm ci` đọc đúng lockfile của mỗi project. Project mở màn cung cấp FFmpeg/ffprobe Windows đi kèm Remotion. Chromium có thể được tải trong lần chạy Remotion đầu tiên.
- Thư mục nguồn gốc chứa `Image/`, `nhạc cưới/` và `wedding folder/`. Các ảnh đã lọc phải khớp [catalog V002](../src/v002/curated.json) về tên và hash. Giữ đúng tên 13 MP3 trong [kịch bản máy đọc](../src/v005/story.json). Template cung cấp lớp hoa, lá và vệt sáng.
- Khôi phục ba font đã dùng vào `projects/wedding-opener/public/fonts/`. Đối chiếu bằng `Get-FileHash -Algorithm SHA256`.

| Font | SHA-256 |
|---|---|
| `CormorantGaramond.ttf` | `b20b7d9626dd956b2c5e558692ad328b1f19e3275e2782db4fa07670d83f35e0` |
| `CormorantGaramond-Italic.ttf` | `0f48ea6abb2084537854f7174c470991a463b13036309e3b50a81511611c530d` |
| `BeVietnamPro-Medium.ttf` | `b60832bfa0fcd015158112c64d7e3fdad3b0c6287d1823f85a3103636e845268` |

## Chuẩn bị từ gốc repo

```powershell
Push-Location projects/wedding-opener
npm ci
Pop-Location

Push-Location projects/wedding-slideshow
npm ci
python -m pip install -r requirements-render.txt
$weddingSource = 'D:\Edit Video Cuoi'
python -B -X utf8 src/v002/prepare.py $weddingSource
python -B -X utf8 src/v005/prepare.py $weddingSource
python -B -X utf8 src/v005/plan.py
node src/v005/lettering.cjs
```

Thay đường dẫn `$weddingSource` bằng vị trí bản sao gốc. Lệnh V002 chuẩn bị các lớp hiệu ứng vào `Source/inbox/wedding-slideshow/v002/overlays` và dùng catalog đã lưu. V005 đối chiếu ảnh và ghép nhạc. Lệnh lập timeline tính mốc ảnh và chữ từ WAV. Node kết xuất lớp chữ và đường cong chuyển động vào `working/v005/`.

## Thử và xuất

Chạy từ `projects/wedding-slideshow`.

```powershell
python -B -X utf8 src/v005/export.py stills
python -B -X utf8 src/v005/export.py sample
python -B -X utf8 src/v005/export.py final --workers 3
python -B -X utf8 src/v005/qa.py
```

Mở ảnh kiểm tra và đoạn 31,12 giây trong `previews/v005/` trước khi xuất cả phim. Bản giao chạy NVENC trên RTX 3060. Khi cần thử xuất bằng CPU, dùng `final --encoder libx264 --workers 1`. Khi render bị ngắt, chạy lại với cùng tham số để script đối chiếu hash và dùng lại đoạn đã đạt. Lần xuất mới cần vị trí `output/wedding-slideshow/van-cong-thuong-huyen-tu-hom-nay-v005.mp4` còn trống.

Bản giao trên máy hiện mang tên `van-cong-thuong-huyen-tu-hom-nay.mp4`. SHA-256 khớp file đã kiểm tra khi xuất. Các lệnh tái tạo vẫn dùng tên có hậu tố `-v005`.

Đã thử từ cây Git sạch trên Windows. Sau khi cài đúng lockfile và bổ sung font, ảnh cùng nhạc, timeline tạo lại khớp V005 và đoạn mở 31,12 giây giải mã được cả hình lẫn tiếng. Phép thử từ cây Git sạch dừng ở đoạn mở. Bản dài đã được xuất và kiểm tra trên máy dựng. Các bản trước V002 có thể cần bộ ảnh nguồn ban đầu. [Quy trình dùng lại](../../../docs/production/workflows/photo-slideshow.md)
