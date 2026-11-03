# Kiểm tra chữ tiếng Việt trong video

Nguồn lỗi và bản sửa: [Yên Thành v003 → v004](../cases/2026-11-03-yen-thanh-tvc.md). Quy tắc này áp dụng khi dựng chữ tiếng Việt, đặc biệt với mask, outline hoặc chia chữ thành các phần để animate.

## Lỗi dễ bỏ sót: dấu bị cắt dù font có glyph

Glyph có thể vẽ phần dấu vượt khỏi hộp layout của một span. `clipPath: inset(0)` hoặc `overflow: hidden` có thể cắt vùng đó. Padding ở div cha không mở rộng vùng clip của span con.

Trong v003, animation kết thúc nhưng `clipPath` trên mỗi `.fx-unit` vẫn còn, nên dấu vẫn mất ở trạng thái đứng yên. Phép đối chiếu dùng cùng font, nội dung, cỡ chữ và line-height đã tái hiện lỗi: cột có clip bị mất dấu, cột không clip hiện đầy đủ. Thay font đơn thuần không chứng minh nguyên nhân đã được xử lý.

## Cách dựng đã dùng ở v004

- Chuẩn hóa Unicode về NFC trước khi chia từ.
- Animate nguyên từ bằng translate/opacity; để overflow của vùng chữ hiển thị đủ ink bounds.
- Nếu cần animate ký tự, chia theo grapheme cluster; giữ dấu đi cùng ký tự nền. Phải kiểm tra font và cách shaping cụ thể.
- Nếu cần mask thực sự, tính vùng mask gồm cả dấu, stroke và chuyển động. Kiểm tra ngay trước khi hoàn tất reveal và trạng thái đứng yên.
- Outline và fill phải dùng cùng font, cỡ, line-height, spacing và cấu trúc chia từ. Hai cấu trúc khác nhau có thể tạo bóng dấu lệch.
- Stroke vẽ phía sau fill; chọn độ dày theo cỡ và độ đậm font để giữ rõ lòng chữ, mũ, móc, hỏi/ngã và dấu nặng.
- Chừa khoảng cách giữa nhãn nhỏ và phần dấu cao nhất của tiêu đề, kể cả trong animation.

V004 dùng Be Vietnam Pro 400/500/600/700, nhấn xanh `#168fe5`, stroke trên footage khoảng 1,6 px ở Full HD và shadow nhẹ. Các thông số thẩm mỹ này thuộc thiết kế Yên Thành; điều chỉnh theo nền và brief của video mới.

## Phép kiểm tra tối thiểu

| Cần xác nhận | Cách kiểm tra | Giới hạn |
|---|---|---|
| Font có glyph | Kiểm tra cmap với đúng ký tự trong nội dung, tải đủ face/weight | Có glyph chưa bảo đảm vùng render không cắt dấu |
| Dấu được vẽ đủ | Xem chữ nhiều dấu trên frame render ở kích thước rõ | Một frame chưa phủ hết animation |
| Dấu đi cùng từ | Xem mẫu frame lúc vào, giữ và ra; bổ sung playback nếu có | Frame lấy mẫu không chứng minh độ mượt liên tục |
| Animation không làm biến dạng chữ sau dừng | So với bản cùng bố cục/font/stroke không animate | Trùng pixel không thay đánh giá thiết kế, cách đọc hoặc audio |
| Bản giao có đúng chữ | Trích và xem lại từ MP4 đã encode | Không dừng ở ảnh Studio hoặc still trước encode |
| Sửa đúng lỗi người dùng | Kiểm tra từng vị trí được báo và lưu ảnh so trước/sau | Không chỉ kiểm tra một câu chữ khác |

Chuỗi kiểm tra gợi ý:

```text
TỰ TIN. TỪ KHỞI ĐẦU.
VỮNG KIẾN THỨC. HIỂU ĐÚNG.
RÈN TỪNG THAO TÁC. SẴN SÀNG CẦM LÁI.
Ă Ằ Ắ Ẳ Ẵ Ặ Â Ầ Ấ Ẩ Ẫ Ậ Ê Ề Ế Ể Ễ Ệ
Ơ Ờ Ớ Ở Ỡ Ợ Ư Ừ Ứ Ử Ữ Ự Đ Ỳ Ý Ỷ Ỹ Ỵ
```

## Bằng chứng tham khảo

- Ảnh trước/sau từ MP4 chỉ có local: `docs/production/evidence/yen-thanh-v004-text-before-after.jpg`; clone repo không có ảnh.
- [Tóm tắt kiểm chứng được lưu cùng docs](../evidence/2026-11-03-yen-thanh-v004.json)
- [Phép tái hiện lỗi cùng font](../../../projects/tvc-driving-premium/src/v004/AccentDiagnosis.tsx)
- [Component kiểm tra dùng TextFx/FillFx production](../../../projects/tvc-driving-premium/src/v004/AccentRegression.tsx)

## Tài liệu tiếng Việt cũng cần QA

Lưu Markdown/JSON bằng UTF-8 rồi đọc lại. Trên Windows, đặt encoding đầu vào/đầu ra shell khi truyền Unicode; `python -X utf8` không phục hồi ký tự đã bị shell đổi thành dấu `?` trước khi tới Python. Với đoạn văn nhiều dấu, dùng cơ chế ghi file giữ nguyên Unicode và kiểm tra nội dung sau ghi.

Các ghi chú cũ của Yên Thành có đoạn đã mất dấu khi tạo qua pipeline shell. Kho kinh nghiệm mới phải dùng bản ghi có dấu được kiểm tra, giữ đường dẫn nguồn kỹ thuật để đối chiếu.
