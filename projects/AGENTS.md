# Các dự án video

Áp dụng [AGENTS gốc](../AGENTS.md) và [workflow](../docs/WORKFLOW.md).

Một guide này áp dụng cho mọi dự án video. Mỗi thư mục con là một video hoặc nhóm bản xuất cùng mục tiêu. Tạo khung bằng `python scripts/studio.py new <id>` từ gốc; template không tự tạo AGENTS cho từng project. Chỉ thêm guide riêng khi project có ngoại lệ thực sự; không lặp lại hướng dẫn chung.

- Trước khi tiếp tục, đọc `project.json`, `brief.md`, `STATUS.md`, `notes/decisions.md` và guide riêng nếu project có. Đường dẫn trong JSON tính từ gốc workspace.
- `src/` chứa code/script dựng; `working/` chứa proxy và bản trung gian; `previews/` chứa ảnh/clip kiểm tra; `notes/` ghi quyết định, shot list và QA.
- Chọn nguyên liệu bằng `assets.json`, không mặc định dùng mọi file inventory tìm thấy. File đầu vào nằm trong `Source/` và giữ nguyên. `sourceRoots` mặc định `["Source"]`, chỉ thu hẹp tới thư mục con khi cần.
- Ảnh AI tạo mới và các bản dẫn xuất riêng của phim nằm trong `working/`, có thể dùng `working/generated/`.
- Cài dependency trong chính project, không ở `projects/` chung hoặc trong repo nguồn tham khảo. Ghi engine và selectedTools vào `project.json`. Khung mới chưa phải app render cài sẵn; bổ sung lệnh tái tạo trong STATUS khi renderer sẵn sàng.
- Preset template là giả định ban đầu; đối chiếu brief trước khi render.
- Bản giao thật ở `output/<id>/` tính từ gốc workspace. Kiểm tra QA, tăng phiên bản khi chỉnh và ghi delivery theo workflow. Không đặt complete chỉ vì tạo khung xong.
- Sau bản giao hoặc vòng phản hồi đáng kể, ghi `notes/retrospective.md` theo mẫu và bổ sung bài học có bằng chứng vào [kho kinh nghiệm sản xuất](../docs/production/README.md). Không thay các quyết định riêng của video bằng kết luận từ một ca khác.
- Git chỉ lưu code, hồ sơ, lockfile và placeholder. Media trong public/working/previews/output được bổ sung hoặc tạo lại trên máy; xem [GIT](../docs/GIT.md). Project mới giữ các thư mục bằng `.gitkeep`; không hiểu trạng thái complete lịch sử là máy vừa clone đã có MP4.
