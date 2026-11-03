# Bổ sung công cụ và quản lý repo tổng

Nếu nâng một công cụ đã có, thực hiện theo [quy trình cập nhật](UPDATING.md). Không tải đè vào thư mục repo con.

## Khi đổi cấu trúc nguyên liệu

Tất cả nguyên liệu dùng chung nằm dưới `Source/`; không tạo lại `footage/`, `images/`, `music/`, `audio/`, `assets/` hoặc `input/` ở gốc. `Source/inbox/` là nơi nhận file mới và `Source/documents/` là chỗ cho yêu cầu/kịch bản/phụ đề.

Inventory mặc định dùng `sourceRoots: ["Source"]`, nên tự tìm cả thư mục con mới. Quy tắc phân loại nằm chung trong Source/AGENTS.md, không tạo guide cho mỗi nhóm media. Nếu thêm nhóm thư mục bắt buộc phải có, cập nhật `INPUT_DIRS` trong `scripts/studio.py`, Source/AGENTS.md, README và workflow. Chỉ thêm guide cấp sâu hơn nếu có quy tắc đặc thù; không bắt validator yêu cầu AGENTS cho mọi thư mục. Nếu di chuyển nguyên liệu đã được project sử dụng, cập nhật đường dẫn tương ứng trong project/code/asset manifest, giữ lựa chọn và hash cũ. Đối chiếu hash trước/sau; không chạy inventory rồi coi những bản đã chuyển là nguyên liệu mới mà bỏ mất lựa chọn cũ.

## Thêm repo thứ 19 trở đi

1. Xác định vấn đề chưa giải quyết được bằng công cụ hiện có. Ưu tiên thêm adapter/package nhỏ khi đủ, không mặc định thêm cả engine.
2. Tải source vào `repos/19-ten-repo/` hoặc số tiếp theo. Xác minh GitHub, license, commit, README, package manifest và API quan trọng.
3. Lưu thông tin nguồn vào `repo-manifest.json`. Để giữ một Git repo tổng, không để `.git` lồng trong `repos/`; lưu metadata Git mới vào `.workspace/upstream-git/` sau khi xác minh đường dẫn nguồn/đích đều nằm trong workspace. Không xoá metadata cũ.
4. Nếu upstream có `AGENTS.md`, lưu nguyên bản vào `docs/upstream-agents/<folder>.md` trước khi tạo hướng dẫn local. Hướng dẫn phát triển thư viện không tự áp dụng cho project video.
5. Thêm mục vào `configs/tools.json`: ID duy nhất, tên, folder, URL, vai trò, khi dùng/không dùng, file đọc đầu tiên, packages, cách nối timeline, lỗi hay gặp và guide upstream nếu có. Nội dung đi theo repo mới; không sao chép mô tả marketing.
6. Cập nhật routing ở `AGENTS.md` và `docs/REPO-MAP.md`. Chạy `python scripts/sync_guides.py`, sau đó `python scripts/studio.py validate`. Sửa registry để sửa guide được sinh tự động.
7. Kiểm tra tải chọn riêng bằng bootstrap trong fixture sạch, đối chiếu commit và guide. Không đưa source upstream vào Git chính. Thử tích hợp nhỏ liên quan rồi mới đưa công cụ vào đường dựng mặc định.

## Nguồn vendored và bản lưu Git

18 repo ban đầu đã được tải vào `repos/` trên máy sản xuất. Repo chính chỉ theo dõi `repos/<folder>/AGENTS.md`; source còn lại bị ignore và được khôi phục theo `repo-manifest.json`. Metadata clone cũ vẫn giữ nguyên ở `.workspace/upstream-git/<folder>.git`, có mapping local trong `configs/upstream-archives.json`. Bootstrap mới lưu metadata tên riêng và `receipt.json` trong `.workspace/bootstrap/<transaction>/`. Các bản lưu local không xuất hiện khi clone repo chính.

`docs/upstream-agents/` giữ các guide gốc; hướng dẫn local trong repo con trỏ lại chúng cho trường hợp phát triển thư viện. Không tự chạy update upstream, không thay source bằng bản mới chỉ để lấy feature chưa cần.

Lần clone ban đầu không fetch submodule hoặc Git LFS riêng. Một gitlink của dotLottie Web (`packages/web/dotlottie-rs`) được ghi trong `configs/upstream-submodules.json`, không nằm trong danh sách file source để stage. Nếu cần build WASM từ source, đọc `.gitmodules` và hướng dẫn upstream rồi tải đúng commit đó; dùng package phát hành không mặc định đòi build lại Rust/WASM. Không coi thư mục gitlink rỗng là mã source đã tải đủ.

Để đối chiếu bản gốc trên máy đang có archive, có thể dùng read-only:

```powershell
git --git-dir=.workspace/upstream-git/05-gsap.git show HEAD:package.json
```

Không khôi phục `.git` vào repo con trong khi vẫn muốn một monorepo. Nếu cần sửa và gửi upstream, dùng checkout/worktree riêng, ngoài đường `repos/` của dự án đang sản xuất, theo quyền filesystem sẵn có.

## Ghi nhận bằng Git

Theo [GIT](GIT.md) để clone, tải source, giữ thư mục trống và kiểm tra phạm vi commit. Chỉ guide/code/cấu hình/tài liệu được đưa lên; media và source upstream ở trên máy. Không force-add danh sách upstream cũ. `download_repos.py` hiện là entrypoint tương thích cho bootstrap khóa commit và không ghi lại manifest theo HEAD.

Thêm công cụ phải đồng bộ registry, manifest, guide và đường tải source. Chỉnh `scripts/check_publish.py` nếu thực sự bổ sung một loại code/tài liệu cần phát hành mới; không nới phạm vi để đưa media vào tiện tay.
