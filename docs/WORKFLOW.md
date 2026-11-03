# Quy trình từ nguyên liệu đến video

Các đường dẫn ví dụ tính từ gốc workspace. AI luôn bắt đầu ở [AGENTS.md](../AGENTS.md) và [REPO-MAP.md](REPO-MAP.md).

## 1. Nhận việc và xem nguyên liệu

Tiếp tục project đang làm nếu người dùng nhắc tới nó; chỉ tạo project mới khi có video mới. `python scripts/studio.py new <id>` tạo hồ sơ theo template. Không dùng tên có dấu/space làm ID; tiêu đề hiển thị vẫn được dùng tiếng Việt.

Đọc [hướng dẫn dự án dùng chung](../projects/AGENTS.md). Mỗi project không cần AGENTS riêng theo mặc định; brief, trạng thái và decisions lưu các yêu cầu cụ thể. Chỉ thêm guide con khi có ngoại lệ đáng kể.

Sau khi clone, nguyên liệu và bản xuất chỉ có thư mục placeholder. Source thư viện cũng được tải riêng theo [GIT](GIT.md). Kiểm tra dữ liệu có thật trên máy trước khi tiếp tục một project lịch sử.

Tất cả nguyên liệu nằm trong `Source/`: `Source/inbox/` nhận file chưa phân loại, `Source/footage/` chứa video, `Source/images/` chứa ảnh, `Source/music/` chứa nhạc, `Source/audio/` chứa voice/SFX, `Source/assets/` chứa tài nguyên và `Source/documents/` chứa yêu cầu/kịch bản/phụ đề. Có thể tạo thư mục con theo đợt quay hoặc dự án. File ở đây là đầu vào; không sửa đè. Thư mục đầu vào bị Git ignore theo thiết kế, nên dùng filesystem để liệt kê. Inventory mặc định quét đệ quy toàn bộ `Source/`; có thể thu hẹp `sourceRoots` của project về các thư mục cụ thể bên dưới `Source/`. Không thêm cả thư mục cha và con nếu không cần. Xem ảnh, xem hoặc trích frame đại diện của clip và nghe tiếng khi cần. Dùng ffprobe đọc duration, resolution, FPS, rotation và audio track. Inventory chỉ nhận diện file, không thay việc hiểu nội dung.

Ghi vào `projects/<id>/brief.md`: mục đích, khán giả, tỷ lệ, thời lượng, nội dung bắt buộc, phong cách, lời thoại/chữ, nhạc và nguồn asset. Điền các giả định có thể đổi trong project. Không đợi một brief hoàn hảo nếu yêu cầu hiện tại đã đủ để làm bản đầu.

## 2. Lập phương án dựng

Viết shot list ngắn trong `notes/shot-list.md`: mỗi cảnh có điểm bắt đầu/kết thúc, nguyên liệu, chữ, tiếng và chuyển cảnh. Chọn asset trong `assets.json`; không đưa tất cả file được quét vào phim. `selected` chỉ ghi nhận lựa chọn của dự án, không phải quyền sử dụng nội dung.

Nếu chưa có source của công cụ đã chọn, chạy `python scripts/bootstrap_repos.py --tool <id>` từ gốc; lệnh giữ nguyên source local đã có. Chọn engine trong `project.json`:

- `ffmpeg`: cắt ghép, crop, resize, audio, chuyển đổi media là trọng tâm.
- `remotion`: text/ảnh/composition/motion graphics cần lập trình.
- `motion-canvas`: animation vector/generator là trọng tâm.
- `custom`: chỉ khi có lý do rõ, ghi trong `notes/decisions.md`.

Điền `selectedTools` bằng ID trong `configs/tools.json`. Chỉ đọc guide cần dùng và tài liệu API liên quan. Không install toàn bộ repo tham khảo.

Tra [kho kinh nghiệm sản xuất](production/README.md) và đọc phần khớp loại video. Với text FX tiếng Việt, áp dụng [kiểm tra font, dấu và vùng clip](production/quality/vietnamese-text.md). Các lựa chọn thẩm mỹ của video mẫu cần được đối chiếu với brief mới.

## 3. Chuẩn bị môi trường và dựng

Chạy `doctor`; thiếu công cụ nào thì xử lý đúng công cụ đó trong phạm vi workspace. Với JS, tạo `package.json` và lockfile trong `projects/<id>/`, dùng package phát hành tương thích. Với FFmpeg, lưu lệnh hoặc script trong `src/` và log trong `working/`. Đường dẫn trong JSON dự án tính từ gốc workspace, không phụ thuộc thư mục hiện hành của shell.

Giữ nguyên liệu gốc ở vị trí cũ. Proxy, audio convert, ảnh resize và physics bake nằm trong `working/`, có thể tạo lại. Font/model/WASM phải load xong trước khi render. Random phải có seed. Timeline video tính bằng frame; quy đổi rõ giây/mili giây/FPS từng nguồn.

Nếu nhiệm vụ cần tạo ảnh bằng AI, lưu kết quả riêng của dự án ở `projects/<id>/working/generated/`, ghi prompt/nguồn liên quan trong notes khi có ích. `Source/images/` dành cho ảnh đầu vào, không dành riêng cho ảnh AI; `Source/inbox/` chỉ là chỗ nhận file chưa phân loại. Khi đã biết loại file, người dùng có thể đưa thẳng vào nhóm phù hợp.

Âm thanh phải nằm trên timeline xuất hoặc mixer thật. Khi có voice-over, đặt nhạc dưới lời, kiểm tra cắt đầu/cuối và audio clipping. Không tạo/đổi giọng hay tự gọi dịch vụ ngoài chỉ vì repo có ví dụ API; làm theo yêu cầu và nguồn có sẵn của dự án.

## 4. Preview và kiểm tra

Lưu preview vào `projects/<id>/previews/`. Kiểm tra ít nhất frame đầu, giữa, cuối và biên chuyển cảnh. Với cảnh có chữ, kiểm tra đủ dấu tiếng Việt, font, line break, vùng an toàn và độ tương phản. Với footage dọc/ngang, xem crop thực tế; không chỉ đổi kích thước một cách máy móc.

Với animation/3D, kiểm tra seek không tuần tự để phát hiện phụ thuộc clock, vật lý hoặc hiệu ứng tích lũy. Nghe audio thật khi công cụ cho phép; nếu chưa nghe được, ghi rõ chưa kiểm tra bằng tai. Không thay thế đánh giá hình/tiếng bằng việc lệnh chạy exit code 0.

Ghi việc đã kiểm tra, kết quả và vấn đề còn lại trong `notes/qa.md`. Sửa lỗi trực tiếp; chỉ xin duyệt khi người dùng yêu cầu bước duyệt hoặc còn quyết định nội dung không thể suy ra.

## 5. Xuất và bàn giao

Xuất `output/<id>/<id>-v001.mp4` hoặc định dạng người dùng yêu cầu. Lần chỉnh sau tăng số phiên bản; không đè bản cũ trừ khi người dùng muốn. Dùng ffprobe xác nhận file đọc được, duration, dimensions, FPS và audio streams theo brief. Xem lại frame/âm thanh sau encode nếu bước encode có thể thay crop, màu hoặc sync.

Lưu `delivery.md` cùng file cuối: yêu cầu đã đáp ứng, danh sách file, lệnh tái tạo hoặc đường dẫn script, preset, nguồn asset cần ghi credit và phần chưa kiểm tra. `delivery.md` không chứa bí mật/token. Đặt trạng thái `complete` chỉ sau khi có output thật đã kiểm tra. Dự án mới tạo bắt đầu `intake`, không phải `complete`.

## 6. Tiếp tục ở lần sau

Đọc `STATUS.md`, `project.json`, brief và decisions trước. Giữ asset selection, các quyết định đã chốt và bản cũ. Bổ sung bản render mới, ghi thay đổi ngắn gọn. Nếu file gốc đã đổi/mất, inventory ghi nhận để xử lý; không âm thầm thay bằng asset khác.

## 7. Ghi bài học sau khi dựng và nhận phản hồi

Điền `notes/retrospective.md` của project theo [mẫu tổng kết](../templates/project/notes/retrospective.md): mục tiêu, công cụ đã chạy thật, phản hồi, nguyên nhân lỗi, cách sửa, bằng chứng và giới hạn.

Chọn 1–3 bài học dùng lại được để thêm vào [docs/production](production/README.md). Giữ hồ sơ theo ca và phiên bản; lưu ảnh/JSON nhỏ quan trọng cùng docs để không phụ thuộc cache bị ignore. Cập nhật quy trình tương ứng khi có bằng chứng, ghi ý tưởng chưa thử vào [danh sách cải tiến](production/IMPROVEMENTS.md), rồi chạy validate. Phản hồi mới có thể sửa kết luận cũ; ghi rõ thay đổi thay vì xóa dấu vết.
