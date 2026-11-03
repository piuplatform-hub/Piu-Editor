# Mã dựng TVC Yên Thành

Bản đang dùng: **v003 — Remotion + GSAP + SVG**.

- `v003/Film.tsx`: composition và hệ text FX.
- `v003/timeline.json`: thời gian các shot, chuyển cảnh và preset.
- `v003/prepare.py`: chuẩn bị footage không tiếng, thiết kế SFX, master soundtrack; kiểm tra hash nguồn.
- `v003/render.cjs`: xuất frame, preview hoặc toàn phim bằng browser đi kèm Remotion.
- `v003/qa.py`: kiểm tra MP4 thật, audio, hash và trích ảnh QA.

Từ thư mục project: `npm run prepare:v003`, `npm run stills:v003`, `npm run preview:v003`, `npm run render:v003`, `npm run qa:v003`. Lệnh render từ chối ghi đè bản giao; khi chỉnh tiếp cần chọn phiên bản mới.

Xem [hướng dẫn tái tạo](../notes/render-v003.md), [brief](../brief.md) và [trạng thái](../STATUS.md).

Code v001 và v002 vẫn được giữ để đối chiếu. `render_ffmpeg.py` là renderer v001 cũ, có tên output v001 cố định; không dùng lệnh đó để tạo bản chỉnh sửa mới. `encode_v002.py` thuộc thử nghiệm v002.
