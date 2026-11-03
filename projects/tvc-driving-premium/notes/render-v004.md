# V004 — sửa dấu tiếng Việt, stroke và xanh nước biển

## Yêu cầu đã triển khai

Người dùng gửi 5 ảnh của v003: dấu tiếng Việt bị cắt ở TỰ TIN, VỮNG KIẾN THỨC, HIỂU ĐÚNG, RÈN TỪNG THAO TÁC và SẴN SÀNG CẦM LÁI. Yêu cầu sửa dấu, thêm stroke và đổi chữ đỏ sang xanh nước biển. Giữ timeline, footage và soundtrack v003.

## Nguyên nhân được tái hiện

`v003/Film.tsx` đặt `clipPath: inset(0 0% 0 0)` lên từng `.fx-unit` sau khi reveal hoàn tất. Glyph có thể vẽ dấu vượt khỏi hộp line-height của span; clipPath cắt theo hộp đó. Padding ở div cha không mở rộng clipPath của span con. Bởi vậy dấu vẫn mất khi chữ đứng yên, không chỉ khi chuyển động.

Composition `AccentDiagnosis` giữ nguyên font Manrope, cỡ chữ, nội dung và line-height ở hai cột. Cột trái có clipPath như v003, cột phải không có. Ảnh `previews/v004/accent-diagnosis.png` tái hiện dấu bị cắt và hồi phục khi bỏ clipPath. Font Manrope cũ có đủ 43 ký tự tiếng Việt được dùng trong phim; đây không phải bằng chứng thiếu glyph.

## Sửa trong v004

- Bỏ clipPath và overflow hidden khỏi hệ chữ; animate nguyên từ đã chuẩn hóa NFC bằng translate, opacity, rotation nhỏ. Dấu đi cùng từ và không có vùng cắt cục bộ.
- Font Be Vietnam Pro 400/500/600/700 tải từ Google Fonts, SHA-256 và URL lưu ở `src/v004/font-sources.json`; license OFL đi kèm asset. Các face này được kiểm tra glyph trong nội dung code.
- Chữ có stroke mảnh vẽ phía sau fill bằng paint-order, cùng shadow nhẹ trên footage; panel sáng dùng viền nhẹ phù hợp.
- Màu nhấn `#168fe5` thay màu đỏ của chữ, nét SVG và graphic transition. Màu đỏ có sẵn trong footage gốc được giữ nguyên.
- Chữ outline-to-fill dùng cùng cấu trúc span và khoảng cách ở cả hai lớp; fill chuyển theo từ bằng opacity, không crop glyph.
- Tăng line-height và kiểm tra lại khoảng cách nhãn, tiêu đề và dấu.

## Tham khảo trên mạng

- [GSAP SplitText masks](https://gsap.com/docs/v3/Plugins/SplitText/masks/): cơ chế wrapper và vùng clip, dùng để đối chiếu với cách reveal. Bản sửa dùng chuyển động không cắt glyph.
- [Be Vietnam Pro tại Google Fonts](https://github.com/google/fonts/tree/main/ofl/bevietnampro): font thật được tải và sử dụng, kèm OFL.
- [Mixkit Kinetic Titles](https://mixkit.co/free-premiere-pro-templates/kinetic/): đã khảo sát; các mẫu ở đây là Premiere Pro/MOGRT. Không tải pack này vào Remotion hoặc tuyên bố đã tích hợp. Text FX được sửa trực tiếp bằng GSAP trong project.

Không nâng source vendored hoặc package để sửa lỗi này.

## Tái tạo

Chạy từ thư mục project:

1. `npm run prepare:v004`: chuẩn bị media bằng cùng timeline/thiết kế âm thanh, kiểm tra hash nguồn; tải font nếu chưa có và đối chiếu SHA-256.
2. `npm run accents:v004`: xuất chữ chạy animation và bản tham chiếu không animate ở cùng bố cục.
3. `npm run stills:v004`: ảnh kiểm tra từ composition đầy đủ.
4. `npm run render:v004`: native Remotion render, PNG → H.264 CRF 16, BT.709 limited, yuv420p, AAC 320 kb/s.
5. `npm run qa:v004`: metadata, full decode, loudness, audio correlation, hash nguồn/bản giao cũ và frame trích từ MP4.

Render từ chối ghi đè MP4 đã có. V003 và các bản cũ giữ nguyên. Snapshot metadata trước sửa ở `working/v004/prior`; hash bản giao cũ ở `working/v004/prior-output-hashes.json`.

## Gate chuyên biệt cho lỗi dấu

- `AccentDiagnosis`: tái hiện lỗi v003 và đối chiếu không clip bằng cùng font.
- `AccentRegression` dùng đúng TextFx/FillFx production và nhiều dấu chồng: Ă/Â/Ê/Ơ/Ư cùng các thanh điệu.
- `AccentReference` dùng cùng glyph, font, stroke và layout nhưng không có GSAP timeline.
- Hai ảnh sau khi animation dừng được so pixel với reference. Không dùng phép so này làm thay thế cho việc xem chữ thật: vẫn xem riêng các frame của năm nhóm người dùng báo, cả khi chuyển động và từ MP4 cuối.

Phép thử render từng frame theo thứ tự khác nhau chỉ xác nhận tính nhất quán ở các frame được lấy mẫu. Chưa nghe duyệt bằng tai hoặc đánh giá playback liên tục trong môi trường trợ lý; soundtrack được giữ nguyên và đối chiếu dữ liệu với v003.
