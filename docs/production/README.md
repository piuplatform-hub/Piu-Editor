# Kho kinh nghiệm sản xuất video

Kho này giúp AI tiếp theo kế thừa cách làm đã có kết quả, hiểu lỗi từng gặp và chọn phần phù hợp với video mới. Bắt đầu từ [AGENTS gốc](../../AGENTS.md) và [WORKFLOW](../WORKFLOW.md); các tài liệu ở đây bổ sung kinh nghiệm thực tế.

## Chọn tài liệu cần đọc

| Công việc | Tài liệu |
|---|---|
| Dựng TVC từ footage, cần typography và chuyển cảnh bằng code | [Quy trình Remotion + GSAP + FFmpeg](workflows/footage-remotion-gsap.md) |
| Có chữ tiếng Việt, mask, stroke hoặc font mới | [Kiểm tra chữ tiếng Việt](quality/vietnamese-text.md) |
| Muốn hiểu cách làm TVC Yên Thành hôm 03/11/2026 | [Hồ sơ Yên Thành v001–v004](cases/2026-11-03-yen-thanh-tvc.md) |
| Tìm phần còn yếu và cơ hội cải tiến | [Danh sách cải tiến](IMPROVEMENTS.md) |
| Ghi bài học sau một video hoặc vòng phản hồi | [Mẫu tổng kết](../../templates/project/notes/retrospective.md) |

Chỉ đọc quy trình và hồ sơ khớp nhiệm vụ. Các video đơn giản vẫn có thể chỉ dùng FFmpeg theo [bản đồ công cụ](../REPO-MAP.md).

## Mỗi loại thông tin có một chỗ

- **Yêu cầu, tiến độ và quyết định của video:** giữ ở `projects/<id>/brief.md`, `STATUS.md`, `notes/`.
- **Hồ sơ đã làm:** thêm một bài trong `cases/`, ghi phiên bản, phản hồi, nguyên nhân lỗi, cách sửa và bằng chứng. Mỗi bài có ngày và phạm vi kết luận.
- **Cách làm dùng lại:** cập nhật `workflows/` hoặc `quality/` sau khi có bằng chứng phù hợp; trỏ về hồ sơ nguồn.
- **Ý tưởng cần thử:** ghi vào `IMPROVEMENTS.md` với điều kiện đánh giá. Chuyển trạng thái khi đã có kết quả thật.
- **Bằng chứng cần giữ cùng tài liệu:** đặt JSON tóm tắt và hash trong `evidence/`. Media so sánh giữ local, không push; ghi đường dẫn và giới hạn khả dụng. Xem [phạm vi Git](../GIT.md).

## Cách tích lũy sau mỗi vòng làm việc

1. Ghi phản hồi của người dùng và phiên bản liên quan vào `notes/retrospective.md` của project.
2. Chọn 1–3 bài học có giá trị dùng lại: điều kiện gặp, thao tác đã làm, kết quả và giới hạn.
3. Nếu lỗi ảnh hưởng bản giao, lưu cách tái hiện và ảnh/receipt sau sửa. Phản hồi mới có thể bác bỏ nhận xét QA cũ; cập nhật kết luận và giữ lịch sử.
4. Thêm hoặc bổ sung hồ sơ trong `cases/`. Chép JSON tóm tắt/hash quan trọng vào `evidence/`; ảnh/video/log vẫn bị Git ignore. Không để bài học chỉ nằm trong cache.
5. Đưa nguyên tắc đã được chứng minh vào đúng quy trình. Giữ các lựa chọn màu, font, nhịp và câu chữ theo phạm vi dự án nếu chưa có lý do áp dụng rộng.
6. Cập nhật mục lục này, danh sách cải tiến nếu cần, rồi chạy `python scripts/studio.py validate`.

Không coi một file render thành công, một bài thử so pixel hoặc một lời khen là xác nhận mọi mặt của video. Ghi riêng: đã đo kỹ thuật, đã xem frame, đã xem chuyển động liên tục, đã nghe, và phản hồi của người dùng.

## Cách phát triển thư viện lâu dài

Sau khi một hiệu ứng hoặc quy trình được dùng tốt trong ít nhất hai dự án có nội dung khác nhau, đánh giá tách thành component/template chung. Giữ nguồn gốc, tham số, mẫu kiểm tra và hướng tái tạo. Đây là tiêu chí cân nhắc, chưa phải thư viện component dùng chung đã được xây.

Thay đổi local trong `docs/production/` được validator kiểm tra link đệ quy. Bản đồ repo và guide sinh tự động vẫn được quản lý qua `configs/tools.json` và `scripts/sync_guides.py` theo [EXTENDING](../EXTENDING.md).
