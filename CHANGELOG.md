# Lịch sử thay đổi

## 2026-11-25 — Phim mở màn và slideshow “Từ hôm nay”

- Lưu code, lockfile và hồ sơ của phim mở màn cùng bản chiếu tiệc V005. Bổ sung quy trình chuẩn bị ảnh, phối 13 bài, dựng chữ ở 50 fps, khôi phục phần xuất gián đoạn và QA MP4.
- Cho phép publish `requirements-render.txt` ở gốc project để giữ phiên bản dependency Python của bản dựng.

## 2026-11-05 — Làm rõ cách AI đọc và hiểu workspace

- Bổ sung hướng dẫn khảo sát mô hình phối hợp 18 công cụ như một đoàn làm phim, xác minh đúng checkout/worktree và báo rõ phạm vi đã đọc hoặc chạy thử.

## 2026-11-03 — Mốc phát triển đầu tiên

- Bản đồ 18 công cụ, hướng dẫn AI, scaffold/inventory/validator và hồ sơ TVC Yên Thành v001–v004.
- Kho kinh nghiệm sản xuất: quy trình Remotion + GSAP + FFmpeg, lỗi mask cắt dấu tiếng Việt và bằng chứng QA dạng JSON.
- Repo Git gọn: source upstream tải riêng theo commit khóa; media, dependency và dữ liệu máy bị ignore; thư mục giữ bằng `.gitkeep`.
- Một lệnh bootstrap cả bộ hoặc chọn công cụ, giữ source local đã có và metadata Git ngoài `repos/`.
- Validator tách kiểm tra repo, source đã tải và media trên máy; kiểm tra Git index trước publish; fixtures và CI Windows/Linux.
- Actions chính chủ được khóa SHA dùng Node 24 sau khi runner cảnh báo Node 20 đã ngừng hỗ trợ; checkout không giữ credential.
- CI Windows phát hiện đường dẫn tạm dạng 8.3; chuẩn hóa cả gốc workspace khi kiểm tra ranh giới đường dẫn và bổ sung fixture chống hồi quy.

Giới hạn: chưa có ứng dụng render chung; chưa xác nhận tái dựng trọn TVC từ clone sạch; QA của ca TVC chưa bao gồm trợ lý nghe audio hoặc xem playback liên tục.
