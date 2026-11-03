# Hồ sơ thực tế: TVC Yên Thành, 03/11/2026

## Kết quả và phạm vi

Đã dựng TVC cho Trung tâm Đào tạo và Sát hạch lái xe Yên Thành bằng footage có sẵn. Bản cuối của phiên làm việc là **v004**, với hệ text FX đã sửa dấu tiếng Việt, thêm stroke và chuyển nhấn đỏ sang xanh nước biển.

Sau khi xem bản sửa, người dùng phản hồi: **“tuyệt! ổn hơn rất nhiều bạn ạ!”**. Đây là phản hồi tích cực cho bản v004; các giới hạn nghe/playback của trợ lý vẫn được ghi riêng.

| Thành phần | Ghi nhận |
|---|---|
| Nguyên liệu đã chọn | 7 clip video + 1 file nhạc; bản gốc giữ nguyên |
| Timeline | 14 đoạn hình, 1920×1080, 24 fps, 975 frame |
| Thời lượng | Video 40,625 giây; container MP4 40,640 giây do biên AAC |
| Bản xuất | H.264 `yuv420p`, BT.709 limited; AAC stereo 48 kHz |
| Âm thanh | Bỏ toàn bộ tiếng footage; nhạc cung cấp + 41 cue SFX tạo bằng code |
| Chữ v004 | Be Vietnam Pro, animation theo từ NFC, stroke mảnh, nhấn `#168fe5` |
| Runtime đã dùng | Remotion và `@remotion/*` 4.0.540, GSAP 3.15.0, React 19.2.0; FFmpeg/ffprobe n7.1 đi kèm dependency |

## Các repo thực sự đóng góp

- **09 Remotion:** dựng composition, Sequence, media, timing và render.
- **05 GSAP:** animation chữ theo chuỗi, easing, stagger, CustomEase và DrawSVG cho nét SVG.
- **18 FFmpeg:** chuẩn bị clip không tiếng, master/mix audio, encode và QA.
- **01 Remotion Skills, 02 GSAP Skills:** hướng dẫn tích hợp, cấu trúc timeline và vòng đời animation.

SVG là định dạng đồ họa sử dụng trong composition. Nhóm Three/Fiber, Satori, SVGO hoặc dotLottie chưa được tích hợp vào bản giao này. Những khả năng đã bàn trước đó thuộc phương án mở rộng.

## Diễn biến và phản hồi

| Phiên bản | Việc đã làm | Kết quả và bài học |
|---|---|---|
| v001 | FFmpeg dựng footage, chữ, nhạc và SFX | Có file giao; người dùng thấy chưa đủ cuốn hút |
| v002 | Thử typography bằng Remotion; từng dùng Player + DOM rasterization để né lỗi browser | Còn dở, chưa có MP4 bàn giao; ghi chú không được coi là chứng minh đã hoàn tất |
| v003 | Render trực tiếp bằng browser đi kèm Remotion; phối GSAP, SVG, 14 shot và 41 cue | Có MP4, QA kỹ thuật đạt; người dùng chỉ ra dấu bị cắt ở 5 nhóm chữ |
| v004 | Bỏ clipPath trên chữ, animate theo từ NFC; Be Vietnam Pro, stroke và xanh nước biển | Đã kiểm tra lại 5 vị trí từ MP4; người dùng phản hồi tích cực |

### Mạch kể và thiết kế

Mở phim bằng xe chuyển động, giới thiệu toàn cảnh trung tâm, đi qua kiến thức → mô phỏng/cabin → đội xe/thực hành → montage → kết thương hiệu. Chữ mỗi cảnh có vai trò riêng; các nét SVG và graphic wipe nối những chương chính.

Điểm cải thiện được người dùng quan tâm nhất là **text FX**. Vì vậy việc dành công sức cho font, dấu, stroke, bố cục và motion của chữ có tác động trực tiếp tới cảm nhận bản giao.

## Lỗi quan trọng: mask cắt dấu

Người dùng gửi ảnh ở các nhóm:

- TỰ TIN / TỪ KHỞI ĐẦU;
- VỮNG KIẾN THỨC;
- HIỂU ĐÚNG;
- RÈN TỪNG THAO TÁC;
- SẴN SÀNG CẦM LÁI.

**Nguyên nhân tái hiện được:** `.fx-unit` của v003 vẫn có `clipPath: inset(0 0% 0 0)` sau khi reveal. Ink của dấu vượt line box nên bị cắt. Padding trên div cha không mở clip của span con. Font Manrope có đủ 43 ký tự tiếng Việt đang dùng; lỗi không chứng minh thiếu glyph.

**Bản sửa:** bỏ vùng cắt cục bộ trên chữ, animate nguyên từ NFC; dùng font Be Vietnam Pro; stroke vẽ sau fill; outline và fill chia từ/khoảng cách giống nhau để không lệch dấu. Giữ vùng dấu thoáng và kiểm tra khoảng nhãn–tiêu đề.

Ảnh so sánh v003/v004 tại năm vị trí báo lỗi được giữ local: `docs/production/evidence/yen-thanh-v004-text-before-after.jpg`. Ảnh không đi kèm khi clone; JSON bên dưới giữ hash và kết quả kiểm tra.

Phép tái hiện cùng font và bản reference không animate giúp xác định nguyên nhân. Việc so 15 frame giữa hai thứ tự render của v003 từng đạt nhưng vẫn bỏ sót lỗi, vì cả hai phía đều render cùng chữ bị cắt. **Tính nhất quán của render phải đi cùng tham chiếu đúng và kiểm tra thị giác.**

## Bài học kỹ thuật

1. **Kiểm tra runtime tại thời điểm làm.** Lỗi browser ở lượt trước không ngăn browser đi kèm chạy được trong lượt sau. V003/v004 dùng native Remotion render; đường DOM capture v002 được giữ làm lịch sử.
2. **Binary có thể nằm trong dependency.** `doctor` kiểm tra PATH không tìm thấy FFmpeg, nhưng `node_modules/@remotion/compositor-win32-x64-msvc` có binary dùng được.
3. **Binary rút gọn cần tham số đúng.** Bản FFmpeg đã dùng không có mọi encoder/muxer mặc định. Decode QA chọn `rawvideo`/`pcm_s16le`; preview M4A cần chỉ rõ `-f mp4` trong script này.
4. **Khai báo color space và kiểm tra MP4.** Encode đầu mặc định báo full range; bản giao được render lại bằng PNG với BT.709 limited và kiểm tra metadata thực tế.
5. **Mỗi phiên bản có code, output và bằng chứng riêng.** V004 giữ hash 8 nguyên liệu và 9 file giao trước đó; soundtrack master giống v003.
6. **PowerShell có thể làm hỏng văn bản trước khi Python ghi file.** Một số ghi chú cũ bị thay dấu thành `?`; lưu UTF-8 và đọc lại nội dung là bước cần làm cho tài liệu tiếng Việt.

## Bằng chứng được giữ

[JSON tóm tắt](../evidence/2026-11-03-yen-thanh-v004.json) được theo dõi trong Git. Ảnh so sánh trong docs và bằng chứng đầy đủ tại `projects/tvc-driving-premium/working/v004/`, `previews/v004/` chỉ có trên máy gốc; media không được push theo chính sách repo. Giữ bản sao riêng nếu cần đối chiếu thị giác sau này.

- Full decode: PASS; đủ 975 frame, đúng preset.
- Audio sau AAC: −14,53 LUFS; true peak −3,60 dBTP. Tương quan master ở 8 kHz: 0,999931, lag 0.
- Font mới: 4 face, 107 ký tự chữ trong nội dung code được kiểm tra, không thiếu glyph.
- Frame 60 và 72 của grid text FX sau dừng trùng pixel reference không animate.
- Đã xem riêng 5 nhóm lỗi từ MP4 mới tại frame 52/220/334/420/530, cùng mẫu frame animation 14/28 và grid dấu.
- Trợ lý chưa nghe bằng tai hoặc xem playback liên tục. Phản hồi của người dùng được ghi riêng, không đổi giới hạn này.
- Chưa kiểm chứng dựng lại từ đầu trên máy khác. Script còn dùng 7 copy clip đầu vào trong `public/video/`; mapping/hash được ghi trong project.

## Điểm vào để tiếp tục hoặc học lại

- [Quy trình chung](../workflows/footage-remotion-gsap.md)
- [Quy tắc chữ tiếng Việt](../quality/vietnamese-text.md)
- [Composition v004](../../../projects/tvc-driving-premium/src/v004/Film.tsx)
- [Chẩn đoán mask](../../../projects/tvc-driving-premium/src/v004/AccentDiagnosis.tsx) và [bài kiểm tra chữ](../../../projects/tvc-driving-premium/src/v004/AccentRegression.tsx)
- [Prepare](../../../projects/tvc-driving-premium/src/v004/prepare.py), [render](../../../projects/tvc-driving-premium/src/v004/render.cjs), [QA](../../../projects/tvc-driving-premium/src/v004/qa.py)
- [Hướng tái tạo](../../../projects/tvc-driving-premium/notes/render-v004.md)

Đường dẫn bản giao trên máy này: `output/tvc-driving-premium/yen-thanh-tvc-v004.mp4`. JSON trong docs lưu hash để đối chiếu; media được Git ignore và không đi kèm tự động khi clone workspace.
