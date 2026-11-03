# Clone, tải source tham khảo và quản lý Git

## Bắt đầu trên máy mới

Cần Git và Python 3.10 trở lên. Chạy:

```powershell
git clone https://github.com/piuplatform-hub/Piu-Editor.git
cd Piu-Editor
python scripts/studio.py validate
python scripts/bootstrap_repos.py
python scripts/studio.py validate --sources
```

Lệnh bootstrap tải cả 18 repo theo commit đầy đủ trong `repo-manifest.json`, không lấy HEAD mới nhất. Có thể chỉ tải công cụ cần dùng:

```powershell
python scripts/bootstrap_repos.py --tool remotion-skills --tool gsap-skills --tool remotion --tool gsap --tool ffmpeg
```

`--list` chỉ liệt kê nguồn và commit. Lệnh cũ `python download_repos.py` chuyển tới cùng bộ tải mới.

Bootstrap không cài package, không build, không tải submodule hoặc Git LFS riêng. Cây nguồn tải xong giữ LICENSE và hướng dẫn local; metadata Git cùng receipt ở `.workspace/`. Lỗi tải trả mã khác 0; thư mục tạm được giữ để chẩn đoán. Chạy lại sẽ bỏ qua repo đã có source, giữ chỉnh sửa local và không tuyên bố đã kiểm chứng lại nội dung đó. Muốn nâng phiên bản, làm theo [UPDATING](UPDATING.md).

## Repo lưu những gì?

| Đưa vào Git | Chỉ lưu trên máy |
|---|---|
| Bản đồ, hướng dẫn, registry, manifest khóa commit | Source upstream tải về trong `repos/`, ngoại trừ `AGENTS.md` local |
| Scripts, tests, templates và kiểm tra CI | Dependency, browser, binary, cache, `.env`, archive Git |
| Code dựng, package manifest/lockfile, brief, quyết định và bài học | Video, ảnh, nhạc, font, model và file giao |
| JSON tóm tắt QA và hash để đối chiếu | Ảnh so sánh/preview, log lớn và dữ liệu trung gian |
| `.gitkeep` để giữ cấu trúc thư mục | Nguyên liệu người dùng tự thêm sau khi clone |

Git không lưu thư mục trống. `.gitkeep` là file rỗng giữ cấu trúc `Source/`, `public/`, `working/`, `previews/`, `output/` và `temp/`. Những dữ liệu đang có trên máy không bị xóa khi thay quy tắc ignore.

Code của TVC Yên Thành được giữ như ca tham khảo có lịch sử v001–v004. Clone repo không mang theo 8 nguyên liệu, font hoặc bản MP4; trạng thái `complete` ghi nhận lần sản xuất trên máy gốc. Đọc `notes/render-v004.md` trước khi dựng lại. Chưa xác nhận dựng trọn TVC từ một clone sạch; xem [PROD-005](production/IMPROVEMENTS.md).

Sau khi clone, người dùng hoặc AI tự bổ sung nguyên liệu vào các nhóm dưới `Source/`, rồi làm theo [WORKFLOW](WORKFLOW.md). File đã ignore cần được lưu trữ/sao lưu riêng.

## Kiểm tra đúng phạm vi

```powershell
python scripts/studio.py validate
python scripts/studio.py validate --sources
python scripts/studio.py validate --local
```

- Mặc định: kiểm tra cấu trúc và tài liệu, registry/manifest, schema project. Chạy được khi chưa tải source hoặc bổ sung media.
- `--sources`: thêm kiểm tra các file `readFirst` và liên kết của 18 source tham khảo. Không xác nhận cây source chưa bị sửa hay runtime hoạt động.
- `--local`: yêu cầu các nguyên liệu đã chọn và file giao lịch sử có trên máy. Không thay thế render, kiểm tra hash hoặc xem/nghe QA.

Hai cờ có thể dùng cùng nhau.

## Trước khi commit/push

```powershell
python scripts/sync_guides.py
python scripts/studio.py validate
python -m unittest discover -s tests -v
git add .
python scripts/check_publish.py
git diff --cached --stat
```

`check_publish.py` đọc chính blob trong Git index, chặn file ngoài phạm vi, media/binary, source upstream, placeholder có nội dung, file trên 2 MiB và một số dạng credential phổ biến. Đây là kiểm tra bổ sung; vẫn cần xem diff trước commit. Không dùng `git add -f` để đưa nguyên liệu hoặc source tham khảo vào repo chính. Hai danh sách cũ `configs/upstream-files.txt` và `upstream-archives.json` chỉ phục vụ đối chiếu trên máy cũ và bị ignore.

Sau khi kiểm tra, commit một thay đổi có mục tiêu rõ rồi push bình thường; không force-push mặc định. CI chạy trên Windows và Linux, kiểm tra bản clone không có media/source, fixtures và guide sinh từ registry.
