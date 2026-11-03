# Lịch sử thay đổi

## 2026-11-03 — Mốc phát triển đầu tiên

- Bản đồ 18 công cụ, hướng dẫn AI, scaffold/inventory/validator và hồ sơ TVC Yên Thành v001–v004.
- Kho kinh nghiệm sản xuất: quy trình Remotion + GSAP + FFmpeg, lỗi mask cắt dấu tiếng Việt và bằng chứng QA dạng JSON.
- Repo Git gọn: source upstream tải riêng theo commit khóa; media, dependency và dữ liệu máy bị ignore; thư mục giữ bằng `.gitkeep`.
- Một lệnh bootstrap cả bộ hoặc chọn công cụ, giữ source local đã có và metadata Git ngoài `repos/`.
- Validator tách kiểm tra repo, source đã tải và media trên máy; kiểm tra Git index trước publish; fixtures và CI Windows/Linux.
- Actions chính chủ được khóa SHA dùng Node 24 sau khi runner cảnh báo Node 20 đã ngừng hỗ trợ; checkout không giữ credential.
- CI Windows phát hiện đường dẫn tạm dạng 8.3; chuẩn hóa cả gốc workspace khi kiểm tra ranh giới đường dẫn và bổ sung fixture chống hồi quy.

Giới hạn: chưa có ứng dụng render chung; chưa xác nhận tái dựng trọn TVC từ clone sạch; QA của ca TVC chưa bao gồm trợ lý nghe audio hoặc xem playback liên tục.
