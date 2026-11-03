# Phát triển Piu Editor

Bắt đầu ở [AGENTS](AGENTS.md), [bản đồ](docs/REPO-MAP.md) và [quản lý Git](docs/GIT.md). Repo hiện là workspace dựng video bằng code và bản đồ chọn công cụ; tiện ích `studio.py` chưa phải ứng dụng render chung.

## Sửa đúng nơi

- Guide sinh tự động: sửa `configs/tools.json` hoặc `scripts/sync_guides.py`, rồi chạy sync. Guide local vẫn có khi source upstream chưa tải.
- Tiện ích/template: sửa trong `scripts/` hoặc `templates/`; thử hành vi có liên quan bằng fixture, không cần chạy test của 18 upstream.
- Code dựng: giữ trong `projects/<id>/src/`, dependency có phiên bản và lockfile trong project. Không commit media trong `public/`.
- Tài liệu: mỗi loại thông tin có một nguồn chính; dùng link để dẫn tới, ghi rõ dữ kiện đã kiểm chứng và ý tưởng chưa thử. Nội dung tiếng Việt phải đọc lại đúng UTF-8.
- Bài học sản xuất: theo [docs/production](docs/production/README.md), giữ lịch sử phản hồi và giới hạn QA.
- Nâng công cụ: theo [UPDATING](docs/UPDATING.md). Bootstrap chỉ khôi phục commit đã khóa, không thực hiện nâng cấp.

## Kiểm tra trước khi gửi thay đổi

```powershell
python scripts/sync_guides.py
python scripts/studio.py validate
python -m unittest discover -s tests -v
```

Sau khi stage, chạy `python scripts/check_publish.py` và xem diff. Có thể chạy `validate --sources` hoặc `--local` khi đã bổ sung dữ liệu tương ứng. Kiểm tra này không chứng minh chất lượng video; sửa composition vẫn cần QA hình/tiếng theo workflow.

Commit nên mô tả một mục tiêu; cập nhật `CHANGELOG.md` cho thay đổi ảnh hưởng cách dùng. Khi có lỗi, ghi cách tái hiện, phạm vi, kiểm tra đã chạy và chỗ chưa xác minh. Thay đổi trong source upstream bị ignore cần chuyển thành patch có chủ đích hoặc commit upstream được ghi vào manifest; không để tri thức chỉ tồn tại trong cây local.
