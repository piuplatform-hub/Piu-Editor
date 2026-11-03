# Hướng dẫn AI cập nhật các công cụ của Piu Editor

Tài liệu này áp dụng khi người dùng nói “kiểm tra cập nhật”, “cập nhật repo X” hoặc “cập nhật nếu cần”. Bắt đầu từ [AGENTS gốc](../AGENTS.md). Thêm công cụ mới theo [EXTENDING](EXTENDING.md); tài liệu này dành cho nâng phiên bản công cụ đã có.

## 1. Xác định việc cần cập nhật

- Đọc [registry](../configs/tools.json), [manifest](../repo-manifest.json) và AGENTS của công cụ được nhắc đến. Xác định repo, commit nguồn hiện tại, chức năng đang sử dụng và các project phụ thuộc.
- Phân biệt **cây nguồn tham khảo trong repos/** với **package/binary chạy thật của project**. Nâng source tham khảo không tự nâng dependency trong project. Không tự sửa lockfile, môi trường hoặc code của project ngoài phạm vi yêu cầu.
- Nếu chỉ được yêu cầu kiểm tra, chỉ kiểm tra và báo kết quả. Nếu được yêu cầu “cập nhật nếu cần”, đánh giá rồi tiến hành phần cập nhật cần thiết trong phạm vi đó; không hỏi lại chỉ vì quy trình này có bước sao lưu hoặc kiểm tra.
- Không tạo một project video chỉ để xử lý yêu cầu bảo trì. Không thay đổi nguyên liệu `Source/` hoặc bản giao `output/`.

## 2. Tìm bản phù hợp và quyết định có nâng không

Kiểm tra GitHub chính chủ, release/tag, changelog và hướng dẫn migration tại thời điểm thực hiện. Ưu tiên release ổn định cho engine; với repo skill không có release, có thể chọn commit cụ thể trên nhánh chính chủ. Ghi lại tag/commit đầy đủ, không chỉ ghi “latest”.

So sánh với bản hiện tại: tính năng thực sự cần, lỗi được sửa, breaking changes, yêu cầu Node/React/Fiber/Three/browser/codec, giấy phép và adapter đi kèm. Không nâng chỉ vì số phiên bản mới hơn. Khi các công cụ phụ thuộc nhau, lập bộ phiên bản tương thích trước, chẳng hạn nhóm Remotion hoặc nhóm Three/Fiber/Drei/Postprocessing.

Nếu chưa có lợi ích cần thiết, giữ bản hiện tại và ghi lý do. Nếu không truy cập được nguồn, không đoán phiên bản hoặc khẳng định đã kiểm tra bản mới.

## 3. Tạo điểm khôi phục trước khi thay thế

1. Kiểm tra trạng thái Git và các thay đổi local. Repo có thể chưa có commit; không coi đó là đã có bản sao lưu.
2. Tạo thư mục riêng như `.workspace/backups/<timestamp>-<tool-id>/`. Sao lưu cây source hiện tại, guide local, guide upstream đã lưu, `repo-manifest.json`, `configs/tools.json`, `configs/upstream-submodules.json` và bản đồ liên quan. Giữ mapping/receipt local nếu có; `upstream-files.txt` và `upstream-archives.json` là dữ liệu cũ chỉ có trên máy gốc, không bắt buộc có sau clone. Nếu nâng project, sao lưu cả package manifest, lockfile và code sẽ sửa của project đó.
3. Ghi danh sách file và hash của bản trước khi nâng, kiểm tra bản sao lưu tồn tại. Có thể tận dụng Git commit hiện có nhưng không tạo commit, sửa history hoặc push chỉ để làm bước sao lưu nếu chưa được yêu cầu.
4. Giữ nguyên các archive Git cũ trong `.workspace/upstream-git/`. Sao lưu local bị Git ignore; muốn mang bản khôi phục sang máy khác phải chuyển riêng hoặc dùng lịch sử Git đã lưu đầy đủ.

## 4. Tải bản mới vào khu vực tạm và so sánh

Clone/checkout đúng tag hoặc commit vào `.workspace/updates/<timestamp>-<tool-id>/`, không clone đè vào `repos/`. Đọc README, manifest, changelog và các API liên quan của bản mới.

Đối chiếu ba phần: bản upstream cũ, source local hiện có và upstream mới. Dùng archive Git cũ nếu có; nếu không có, tải đúng commit cũ ghi trong manifest vào khu vực tạm. Phát hiện mọi chỉnh sửa local, không chỉ `AGENTS.md`; giữ hoặc chuyển tiếp các patch cần thiết. Giải quyết xung đột dựa trên chức năng dự án đang cần, không âm thầm loại bỏ thay đổi local.

Hướng dẫn local được sinh từ `configs/tools.json`, nên không lấy AGENTS upstream mới ghi đè trực tiếp. Nếu upstream có AGENTS mới, cập nhật bản lưu trong `docs/upstream-agents/<folder>.md`, đồng thời lưu bản cũ trong backup. Kiểm tra lại đường dẫn `readFirst`, API và nội dung registry khi source mới đổi cấu trúc.

## 5. Thay source và cập nhật bản đồ đồng bộ

- Chỉ thay sau khi đã có backup và xác định được bản mới. Thay toàn bộ snapshot có kiểm soát, bao gồm xử lý file upstream đã xoá; copy đè kiểu trộn thư mục có thể để sót file cũ. Trước khi move hoặc xoá đệ quy, xác minh đường dẫn tuyệt đối của cả nguồn/đích đều thuộc đúng khu vực workspace cần thao tác.
- Giữ một Git repo ở gốc. Metadata `.git` của clone mới cần lưu vào archive có tên/version riêng; không đặt `.git` trong repo con, không ghi đè hoặc xoá archive cũ. Cập nhật mapping archive đang dùng cho snapshot mới, giữ mapping trước đó trong backup/log.
- Ghi commit/tag/branch, ngày đồng bộ, commit date và số file đúng cho mục repo trong `repo-manifest.json`; giữ thông tin lịch sử trong log. Không sửa lại `review-evidence.json` để giả rằng khảo sát ban đầu đã kiểm tra bản mới.
- Source upstream không được Git chính theo dõi. Ghi receipt/mapping metadata mới trong `.workspace/`, giữ bản cũ; không force-add source theo `upstream-files.txt`. Cập nhật commit/URL trong manifest để người clone tải đúng bản đã nâng. Gitlink/submodule ghi riêng trong `configs/upstream-submodules.json`, không coi thư mục rỗng là file đã tải.
- Giữ LICENSE/COPYING và ghi trạng thái submodule/LFS. Chỉ tải thêm thành phần khi công việc/build cần đến; ghi rõ những thành phần chưa tải.
- Chỉnh `configs/tools.json` và routing trong AGENTS gốc nếu vai trò/cách dùng thay đổi. Chạy `python scripts/sync_guides.py` để tạo lại guide con và bản đồ. Không sửa tay guide được sinh rồi bỏ quên registry.

## 6. Nếu nâng công cụ chạy thật của một project

Chỉ làm bước này khi nhiệm vụ cần nâng runtime hoặc người dùng đã yêu cầu. Chọn phiên bản tương thích và dùng package manager/lockfile của chính project. Không install tất cả thư viện trong `repos/`.

Các package `remotion` và `@remotion/*` cần cùng phiên bản; kiểm tra peer dependencies React/Fiber/Drei/Three/Postprocessing và runtime của Mediabunny. Với FFmpeg, phiên bản cây source C và phiên bản binary trong PATH là hai thông tin khác nhau; tải source mới không nâng binary. Ghi lại binary/package thực sự chạy khi kiểm tra.

Thử phần bị ảnh hưởng: build/typecheck phù hợp, render một đoạn hoặc vài frame đại diện, kiểm tra text/font, crop, timing, audio và codec liên quan. Với cảnh có state/vật lý, kiểm tra seek không tuần tự. Nếu chưa có app tích hợp để chạy, ghi “chỉ cập nhật/kiểm tra source”, không tuyên bố runtime đã hoạt động.

## 7. Kiểm tra, ghi kết quả và khôi phục khi cần

Chạy từ gốc:

```powershell
python scripts/sync_guides.py
python scripts/studio.py validate
python scripts/studio.py validate --sources
```

`validate` kiểm tra cấu trúc, đường dẫn và dữ liệu; `--sources` yêu cầu đủ file đọc đầu tiên của cả bộ source. Nếu chỉ tải một công cụ, kiểm tra file `readFirst` của riêng công cụ đó và ghi rõ chưa chạy gate toàn bộ. Không thay thế build/render test. Kiểm tra thêm đúng chức năng bị thay đổi, không chạy toàn bộ test của 18 dự án khi không liên quan.

Ghi kết quả tại `docs/updates/<YYYY-MM-DD>-<tool-id>.md` (thêm số nếu trùng): lý do, tag/commit cũ → mới, source/runtime nào đã đổi, patch local đã giữ, vị trí backup/archive, lệnh và kết quả kiểm tra, phần chưa kiểm tra và cách khôi phục. Cập nhật STATUS/decisions của project nếu project bị tác động.

Nếu bản mới làm hỏng chức năng cần dùng, khôi phục snapshot cùng guide, registry, manifest, danh sách tracked file và mapping từ bản sao lưu; nếu đã nâng project thì khôi phục cả dependency/code tương ứng. Chạy lại kiểm tra liên quan, báo rõ cập nhật không thành công. Không chỉ khôi phục source mà để metadata trỏ sang bản mới.

Khi bàn giao, nêu công cụ nào đã nâng hoặc được giữ nguyên, lý do, kiểm tra đã chạy và giới hạn còn lại. Không tự commit/push hoặc phát hành trong quy trình này.
