# Danh sách cải tiến sản xuất

Ngày bắt đầu: 03/11/2026. Cập nhật bằng kết quả và phản hồi thực tế. `Đã áp dụng` nghĩa là đã có thay đổi trong phạm vi nêu; các mục `Đề xuất` chưa được coi là tính năng đang có.

| ID | Trạng thái | Việc cần giữ hoặc cải tiến | Bằng chứng / điều kiện đánh giá |
|---|---|---|---|
| PROD-001 | Đã áp dụng cho chữ tiếng Việt | Kiểm tra glyph, vùng clip, stroke và đúng vị trí người dùng báo | [Lỗi mask Yên Thành](cases/2026-11-03-yen-thanh-tvc.md); [quy trình QA](quality/vietnamese-text.md) |
| PROD-002 | Đã áp dụng cho kho tài liệu | Mục lục, hồ sơ có bằng chứng nhỏ và mẫu tổng kết theo project | [Điểm vào](README.md); link tài liệu con được validator kiểm tra |
| PROD-003 | Đề xuất | Tách component TextFx/FillFx/Road thành bộ mẫu dùng chung | Thử ở ít nhất hai project khác nội dung; kiểm tra tiếng Việt, nền sáng/tối, khung ngang/dọc và seek trước khi chốt API |
| PROD-004 | Đề xuất | Đồng bộ toàn bộ mốc hình/chữ/SFX từ timeline chung | Thay một điểm cắt trong fixture; ảnh, chuyển cảnh và SFX cùng dịch đúng frame; giữ tổng frame và phiên bản cũ |
| PROD-005 | Đề xuất | Dựng lại được từ Source + manifest + lockfile | Ca hiện tại còn đọc copy clip ở public/video. Thử trong working mới, khôi phục mapping và đối chiếu hash; không sửa hoặc bỏ bản cũ để thử |
| PROD-006 | Còn giới hạn | Bổ sung xem playback và nghe QA ở môi trường hỗ trợ | Ghi người/công cụ đã xem/nghe và vấn đề phát hiện; không dùng full decode hoặc waveform để thay đánh giá cảm nhận |
| PROD-007 | Đã ghi quy tắc; cần tiếp tục áp dụng | Văn bản tiếng Việt được ghi và đọc lại đúng UTF-8 | File mới giữ nguyên dấu; các ghi chú lịch sử hỏng dấu chỉ sửa khi có nguồn khôi phục rõ ràng |

## Cách thêm một mục

Ghi vấn đề thấy trong video thật, tác động tới người xem hoặc khả năng tái tạo, trạng thái, ca nguồn và phép thử có thể kết luận. Ưu tiên lỗi lặp lại hoặc mất nhiều thời gian. Một ý tưởng sáng tạo mới có thể thử trong project riêng; chỉ đưa thành mặc định khi kết quả phù hợp.

Khi hoàn thành: ghi ngày, phạm vi, bằng chứng và link code/hồ sơ; cập nhật quy trình liên quan. Giữ lịch sử khi một kết luận bị phản hồi mới bác bỏ. Các mục ở đây không tự cấp quyền nâng package, gọi dịch vụ trả phí, xuất bản hoặc sửa mọi project.
