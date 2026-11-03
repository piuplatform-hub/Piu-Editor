# Kiểm tra chất lượng — v001

- `python projects/tvc-driving-premium/src/render_ffmpeg.py`: exit 0. Log ở working/picture-render.log.
- Đã xem contact sheet 5 thời điểm cho cả 7 nguồn. Đã xem 4 frame thiết kế trước render; sau chỉnh font thứ cấp và bỏ điểm đỏ thừa ở outro, đã xem frame MP4 cuối ở 3,5 / 18,2 / 23,8 / 39,2 giây.
- Chữ tiếng Việt có đủ dấu, không tràn khung, tương phản tốt với graduated navy overlay. Các dòng xuất hiện lệch nhịp có chủ đích, không đồng loạt phủ kín footage.
- Giữ khung ngang nguồn, letterbox 82 px trên/80 px dưới; không stretch hoặc crop đổi tỉ lệ. Timeline có 14 shot theo lưới nhịp khoảng 124 BPM.
- FFprobe: H.264 yuv420p, 1920×1080, 24/1 fps, thời lượng 40,625 giây; một video stream và một AAC stereo 48 kHz. Decode toàn bộ MP4 bằng FFmpeg exit 0, không lỗi decode.
- Source audio đã bị loại ở montage (`-an`), ffprobe edit-base chỉ có video. Bản xuất chỉ map audio từ soundtrack mới, không map audio footage.
- Master WAV: -15,00 LUFS, -3,07 dBTP. MP4 AAC sau encode: -15,02 LUFS, -3,11 dBTP. Không clipping theo đo true peak; nhạc và 45 cue SFX có timing/gain tái tạo được.
- SHA256 của 8 file được dùng (7 footage + 1 nhạc) khớp manifest ban đầu, không chỉnh nguyên liệu.
- Giới hạn: môi trường không hỗ trợ audio input cho mô hình, nên chưa nghe duyệt bằng tai. Không ghi nhận đã kiểm tra cảm giác nghe/nhạc/SFX theo cách đó. Không có hotline/brand guideline riêng và không xác minh quyền phát hành nhạc do người dùng cung cấp.
- Bản giao đủ để người dùng xem/nghe bản đầu; chưa tự đăng tải/phát hành. Dữ liệu đo đầy đủ: working/final-qa.json và working/audio-source-qa.json.

## V003 ? b?n cu?i

- Native render Remotion + GSAP/DrawSVG, kh?ng browser error; ?? 975 frame.
- 15 frame xu?t ri?ng theo th? t? kh?c nhau tr?ng t?ng pixel v?i ?nh ki?m tra.
- ?? xem 15 khung thi?t k?, chu?i frame ?o?n m?, frame MP4 v? 12 khung quanh 4 graphic transition. Ch?nh kho?ng c?ch nh?n m? ph?ng v? lo?i vi?n l?u l?i sau fill.
- File cu?i BT.709/tv/yuv420p, 1920?1080, 24/1 fps, 975 frame; container 40,640 gi?y; m?t H.264 v? m?t AAC stereo 48 kHz. Full decode PASS.
- ?m thanh sau AAC: -14.53 LUFS, -3.60 dBTP; t??ng quan master 0.999931, lag 0. ??y l? ?o k? thu?t, ch?a nghe b?ng tai.
- SHA-256 8 nguy?n li?u kh?p; 7 copy input kh?p ngu?n; 14 ?o?n chu?n b? kh?ng c? audio. File b?n giao c? kh?p baseline hash.
- B?o c?o: working/v003/qa-report.json; l?nh t?i t?o: notes/render-v003.md.
- Gi?i h?n: ch?a xem playback li?n t?c ho?c nghe duy?t; ng??i d?ng duy?t nh?p, text FX, mix v? n?i dung tr??c ph?t h?nh.

## V004 ? l?i d?u, stroke, xanh n??c bi?n

- T?i hi?n clipPath inset(0) c?a v003 c?t ph?n d?u v??t line box; c?ng font kh?ng clip hi?n ?? d?u.
- Font Be Vietnam Pro: 4 face, 107 k? t? ch? ki?m tra kh?ng thi?u glyph.
- AccentRegression d?ng TextFx/FillFx th?t; frame 60 v? 72 tr?ng pixel AccentReference kh?ng animate. ?? xem frame 14/28 trong l?c chuy?n ??ng v? grid c?c thanh ?i?u.
- 5 nh?m ch? l?i ?? ???c xem l?i t? MP4 m?i t?i frame 52/220/334/420/530. D?u ??y ??, stroke nh?, nh?n xanh.
- MP4 ?? 975 frame, Full HD 24 fps, BT.709 limited; full decode PASS. -14,53 LUFS / -3,60 dBTP; audio t??ng quan master 0,999931.
- Master v004 gi?ng h?t master v003; 8 nguy?n li?u v? 9 file b?n giao tr??c s?a kh?p hash.
- Ch?a nghe b?ng tai ho?c xem playback li?n t?c; kh?ng coi so pixel l? thay th? ??nh gi? c?m gi?c chuy?n ??ng.
