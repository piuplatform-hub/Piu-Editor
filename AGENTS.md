# Piu Editor — chỉ dẫn cho AI

Workspace này biến nguyên liệu của người dùng thành video theo yêu cầu. Đường dẫn trong tài liệu tính từ gốc repo, trừ link Markdown tương đối. Giao tiếp với người dùng bằng tiếng Việt dễ hiểu.

## Phân cấp hướng dẫn

- Gốc repo có một `AGENTS.md` tổng; mỗi repo công cụ trong `repos/` có một file riêng cho cách dùng công cụ đó.
- [Source/AGENTS.md](Source/AGENTS.md) dùng chung cho toàn bộ nguyên liệu; [projects/AGENTS.md](projects/AGENTS.md) dùng chung cho các dự án video. Các thư mục ảnh, nhạc, output, temp và template không cần file riêng theo mặc định.
- Chỉ thêm `AGENTS.md` ở cấp sâu hơn khi có quy tắc riêng đáng kể; chỉ ghi phần khác biệt. Yêu cầu và tiến độ của từng video nằm trong `brief.md` và `STATUS.md`, không tạo AGENTS cho mỗi project theo quán tính.
- Repo chính chỉ lưu guide, code, cấu hình, tài liệu và placeholder; không push media hoặc source upstream. Sau clone, tải source cần dùng bằng `python scripts/bootstrap_repos.py --tool <id>`, hoặc bỏ `--tool` để tải cả bộ. Đọc [GIT](docs/GIT.md) trước khi stage/push; không tải đè source đã có.
- Khi bỏ hoặc thêm guide, cập nhật link và validator; không sao chép nguyên hướng dẫn cấp cha xuống các thư mục con.

## Khi được yêu cầu đọc và hiểu repo

Piu Editor kết hợp 18 công cụ như một đoàn làm phim. AI điều phối từ yêu cầu video: chia công đoạn, chọn công cụ phù hợp, nối kết quả và kiểm tra bản phim hoàn chỉnh. Mỗi video hoặc cảnh có thể dùng một vài công cụ; các repo có thể bổ trợ hoặc thay thế nhau trong cùng công đoạn.

1. Xác minh thư mục đang mở, gốc Git, worktree và đường dẫn người dùng chỉ định. Nếu có nhiều bản checkout, đối chiếu đúng bản trước khi kết luận; luôn ghi rõ phạm vi thư mục đã khảo sát.
2. Đọc bản đồ công cụ, workflow và registry để nắm vai trò của đủ 18 công cụ, cách chọn và phối hợp chúng. Giải thích được công cụ nào phụ trách phần nào và cách đưa kết quả về cùng bản dựng.
3. Liệt kê filesystem tại thư mục thực tế, kể cả file bị Git ignore. Phân biệt hướng dẫn local, source upstream, dependency đã cài, nguyên liệu và output hiện có. Tình trạng của một worktree chỉ là bằng chứng cho worktree đó.
4. Đọc guide con trước, rồi khảo sát tài liệu và điểm tích hợp trong source liên quan. Chọn độ sâu theo nhiệm vụ hoặc yêu cầu của người dùng; tổng quan cả bộ không đòi hỏi đọc toàn bộ mã nguồn của 18 thư viện.
5. Dùng project sẵn có làm ví dụ về cách phối hợp công cụ, đồng thời giữ phần đánh giá tổng thể của workspace. Khi tổng kết, nêu mục tiêu sản xuất, cách chọn/phối hợp công cụ, dữ liệu hiện có và giới hạn đã xác minh. Ghi riêng hướng dẫn đã đọc, source đã khảo sát và runtime đã chạy thử.

Với yêu cầu chỉ đọc và hiểu repo, bàn giao kết quả khảo sát. Việc tạo project, cài dependency hoặc render được thực hiện khi nhiệm vụ cần đến.

## Khi người dùng yêu cầu cập nhật công cụ

Đọc [UPDATING](docs/UPDATING.md) trước khi kiểm tra hoặc nâng repo con. Không tải đè: xác minh phiên bản, sao lưu, so sánh và giữ chỉnh sửa local, thay source có kiểm soát, cập nhật guide/manifest/registry rồi kiểm tra. Phân biệt cập nhật source tham khảo với nâng package/binary của project. Với yêu cầu “cập nhật nếu cần”, đánh giá lợi ích/tương thích rồi thực hiện phần cần thiết trong phạm vi đã yêu cầu; không tự nâng toàn bộ 18 repo. Thêm repo mới theo [EXTENDING](docs/EXTENDING.md). Đây là công việc bảo trì, không cần tạo project video.

## Bắt đầu một yêu cầu

1. Đọc [bản đồ chọn công cụ](docs/REPO-MAP.md) và [quy trình làm video](docs/WORKFLOW.md). Tra [kho kinh nghiệm sản xuất](docs/production/README.md) để chọn quy trình/hồ sơ khớp nhiệm vụ; với chữ tiếng Việt, đọc bài kiểm tra dấu trước khi dựng text FX. Chỉ mở hướng dẫn của repo cần dùng; không nạp toàn bộ 18 repo.
2. Kiểm tra `projects/` để tiếp tục đúng dự án. Với dự án mới, chạy `python scripts/studio.py new <project-id> --title "Tên video"`. Đây là khung dự án, chưa phải app render.
3. Tìm nguyên liệu trong `Source/`: `inbox/` cho file chưa phân loại, `footage/` video, `images/` ảnh, `music/` nhạc, `audio/` voice/SFX, `assets/` font/logo/model và `documents/` brief/kịch bản/phụ đề. Các tên con này đều nằm dưới `Source/`, không nằm ngang hàng với nó. Có thể có file bị Git ignore; dùng liệt kê filesystem, không chỉ dựa vào `git ls-files` hoặc `rg --files` mặc định.
4. Chạy `python scripts/studio.py inventory --project <project-id> --hash` để ghi danh sách nguyên liệu. Đọc brief, xem ảnh/đoạn video liên quan, dùng ffprobe kiểm tra media. Không đoán nội dung chỉ từ tên file.
5. Ghi mục tiêu, tỉ lệ khung hình, thời lượng, nhịp, nội dung chữ, tiếng và giả định vào `projects/<project-id>/brief.md`; chọn các asset thật sự dùng trong `assets.json` (`selected: true`). Nếu người dùng đã nêu yêu cầu thì thực hiện, không hỏi lại. Chỉ hỏi thông tin thiếu khi nó ngăn việc làm đúng.
6. Chọn công cụ tối thiểu theo bảng bên dưới. Đọc `repos/<tên>/AGENTS.md` trước khi sử dụng hoặc sửa repo đó.
7. Dựng trong `projects/<project-id>/src/`; proxy/bản trung gian trong `working/`; ảnh kiểm tra/bản nháp trong `previews/`. Bản giao nằm ở `output/<project-id>/`. Cập nhật `STATUS.md`, `project.json`, `notes/decisions.md` để lần sau tiếp tục được.
8. Làm preview, kiểm tra hình/tiếng, render bản cuối theo [WORKFLOW](docs/WORKFLOW.md). Không tuyên bố đã render hoặc đã kiểm tra nếu chưa chạy thật.

## Chọn đúng công cụ

| Nhu cầu | Đọc hướng dẫn |
|---|---|
| Cắt, ghép, crop, đổi kích thước, tốc độ, âm lượng video có sẵn | [FFmpeg](repos/18-ffmpeg/AGENTS.md) |
| Dựng chữ, ảnh, nhiều cảnh, phụ đề, motion graphics bằng React | [Remotion Skills](repos/01-remotion-skills/AGENTS.md), [Remotion](repos/09-remotion/AGENTS.md) |
| Timeline chuyển động DOM/SVG phức tạp | [GSAP Skills](repos/02-gsap-skills/AGENTS.md), [GSAP](repos/05-gsap/AGENTS.md) |
| Animation DOM/SVG với Anime.js, hoặc code có sẵn dùng nó | [Anime.js](repos/06-animejs/AGENTS.md) |
| Animation/gesture/layout trong giao diện web, hoặc code có sẵn dùng Motion | [Motion](repos/07-motion/AGENTS.md) |
| Tối ưu SVG / sinh card chữ hoặc đồ hoạ tĩnh theo template | [SVGO](repos/03-svgo/AGENTS.md) / [Satori](repos/04-satori/AGENTS.md) |
| Asset `.lottie` hoặc Lottie JSON | [dotLottie](repos/08-dotlottie-web/AGENTS.md) |
| Animation vector/bài giảng bằng generator TypeScript | [Motion Canvas](repos/10-motion-canvas/AGENTS.md) |
| Scene/model/ánh sáng/camera 3D | [Three.js](repos/11-threejs/AGENTS.md), [Fiber](repos/12-react-three-fiber/AGENTS.md), [Drei](repos/13-drei/AGENTS.md) |
| Va chạm, rơi, nảy vật lý | [Rapier](repos/14-rapier/AGENTS.md) |
| Bloom, depth of field, LUT, hậu kỳ cảnh Three.js | [Postprocessing](repos/15-postprocessing/AGENTS.md) |
| Nghe thử âm thanh trong app web | [Howler.js](repos/16-howlerjs/AGENTS.md) |
| Đọc/ghi/chuyển đổi media trong JS/browser/server | [Mediabunny](repos/17-mediabunny/AGENTS.md) |

## Quy tắc sản xuất

- Giữ file gốc nguyên vẹn. Không ghi đè, đổi tên, di chuyển hoặc xoá nguyên liệu khi chưa được người dùng yêu cầu; tạo bản dẫn xuất trong dự án. Bỏ qua symlink dẫn ra ngoài workspace khi quét nguyên liệu.
- Dùng FFmpeg cho việc cắt ghép đơn giản; Remotion cho composition bằng code. Không bắt buộc dùng đủ 18 repo. Motion Canvas là engine thay thế hoặc tạo clip riêng để ghép vào timeline chính.
- `repos/` chứa guide được theo dõi và source tham khảo tải riêng theo manifest, không phải thư mục chứa project video. Cài dependency trong dự án cần dùng; không chạy install/build toàn bộ 18 thư viện. Các lệnh phát triển upstream chỉ dành cho sửa chính thư viện đó.
- Một chuẩn thời gian cho video: FPS, độ dài, frame của scene. Với Remotion, trạng thái hình phải theo `useCurrentFrame()` hoặc dữ liệu đã bake. Không dùng clock thực, autoplay hoặc random không seed trong bản xuất.
- Âm thanh phải có đường export/mix thật. Howler hoặc tiếng đang phát trong browser không tự đi vào MP4.
- Chờ ảnh/font/model/WASM tải xong trước khi chụp frame. Khóa phiên bản dependency; các package Remotion cùng phiên bản; kiểm tra React/Fiber/Drei/Three tương thích.
- Nếu cần dịch vụ tạo ảnh, giọng nói, nhạc hoặc upload, xác định dịch vụ và dữ liệu cần gửi theo yêu cầu người dùng; bộ repo này không tự cung cấp các dịch vụ đó.
- QA tối thiểu: khung đầu/giữa/cuối và các điểm chuyển cảnh; chữ tiếng Việt, crop, aspect ratio; nghe âm thanh; ffprobe kiểm tra duration, resolution, FPS, audio; so kết quả với brief.
- Chỉ coi công việc hoàn tất khi có file đầu ra thật và ghi lại giới hạn/chỗ chưa kiểm tra. Yêu cầu chỉ tổ chức repo/tài liệu thì không cần tự render video.
- Sau bản giao hoặc phản hồi đáng kể, điền `notes/retrospective.md` theo mẫu project. Lưu bài học có bằng chứng vào [kho kinh nghiệm](docs/production/README.md); ghi phạm vi và phần chưa thử. Giữ lịch sử khi phản hồi mới sửa kết luận QA cũ.

## Bản đồ thư mục và bảo trì

- [README](README.md): cách người dùng thả file và yêu cầu dựng.
- [REPO-MAP](docs/REPO-MAP.md): chọn công cụ, phối hợp, ví dụ.
- [WORKFLOW](docs/WORKFLOW.md): các bước từ brief đến bản giao.
- [Kinh nghiệm sản xuất](docs/production/README.md): quy trình dùng lại, hồ sơ video, lỗi đã gặp và hướng cải tiến có bằng chứng.
- [tools.json](configs/tools.json): danh mục công cụ có cấu trúc; nguồn tạo 18 hướng dẫn con.
- [EXTENDING](docs/EXTENDING.md): thêm repo mới, sửa hướng dẫn và quản lý Git.
- [UPDATING](docs/UPDATING.md): kiểm tra bản mới, nâng có sao lưu, giữ hướng dẫn local, xác minh và khôi phục.
- [GIT](docs/GIT.md): clone, khôi phục source và phạm vi commit; [CONTRIBUTING](CONTRIBUTING.md): cách phát triển và kiểm tra.
- [PROJECTS](projects/AGENTS.md): hướng dẫn chung cho các project; [template](templates/project/): mẫu hồ sơ dự án mới, không tự tạo AGENTS riêng.
- [repo-manifest](repo-manifest.json): nguồn và commit upstream lúc tải; [review-evidence](review-evidence.json): dấu vết khảo sát ban đầu, không phải bằng chứng nội dung hiện tại chưa đổi.

Chạy `python scripts/studio.py validate` sau khi thay bản đồ/thư mục/registry. Mặc định chỉ kiểm tra repo; thêm `--sources` để kiểm tra file của source đã tải, `--local` để kiểm tra nguyên liệu đã chọn và file giao trên máy. Nếu sửa nội dung `configs/tools.json`, chạy `python scripts/sync_guides.py` rồi validate. Trước commit/push, chạy `python scripts/check_publish.py` sau khi stage. Không cập nhật source upstream hàng loạt tự động; giữ LICENSE và ghi lại bản cập nhật có chủ đích.

Các script workspace dùng Python standard library, lấy ROOT từ vị trí file thay vì cwd, kiểm tra đường dẫn và giữ nguyên input. Sau sửa tiện ích/template, thử hành vi liên quan trong fixture rồi validate. Không đặt nguyên liệu vào template; `{{...}}` là placeholder được thay khi tạo project. `temp/` chỉ chứa dữ liệu có thể tạo lại. `.workspace/upstream-git/` chứa archive cần giữ để đối chiếu, không phải cache để tự xoá.
