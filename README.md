# Piu Editor

Đây là nơi đưa video, ảnh, nhạc gốc vào để AI dựng thành video theo yêu cầu. Repo chứa bản đồ 18 công cụ, hướng dẫn AI, tiện ích quản lý và code dựng tham khảo. Source của 18 công cụ được tải riêng bằng một lệnh; nguyên liệu và video được thêm sau khi clone.

Đã có ca sản xuất TVC Yên Thành dùng Remotion + GSAP + FFmpeg, cùng bài học sửa dấu tiếng Việt. Chưa có ứng dụng render chung hoặc bộ dependency cài sẵn cho mọi công cụ.

## Bắt đầu sau khi clone

Cần Git và Python 3.10 trở lên:

```powershell
git clone https://github.com/piuplatform-hub/Piu-Editor.git
cd Piu-Editor
python scripts/studio.py validate
python scripts/bootstrap_repos.py
```

Lệnh cuối tải cả 18 source theo commit khóa, giữ nguyên source local đã có. Có thể chọn từng công cụ bằng `--tool remotion --tool gsap`. Không tự cài dependency, tải nguyên liệu hoặc render. Xem [hướng dẫn Git và khôi phục source](docs/GIT.md).

## Bạn dùng như thế nào?

1. Copy file vào một trong các thư mục con của `Source/` bên dưới. Nếu chưa muốn phân loại, thả tất cả vào `Source/inbox/`.
2. Nói với AI điều bạn muốn làm: nội dung, video dọc/ngang, thời lượng, chữ, giọng đọc và phong cách nếu đã có ý tưởng.
3. AI đọc `AGENTS.md`, kiểm tra nguyên liệu, tạo một project riêng, chọn công cụ và dựng video. Khi việc dựng hoàn tất, file giao nằm trong `output/<tên-dự-án>/`.

Ví dụ yêu cầu:

> Dùng ảnh trong Source/images và nhạc trong Source/music, dựng video dọc 30 giây giới thiệu quán cà phê. Nhịp nhẹ, chữ tiếng Việt, cuối video hiện địa chỉ. Giữ file gốc và cho mình một bản MP4.

> Dùng Source/footage/san-pham để cắt video 60 giây thành bản 20 giây, bỏ đoạn chờ, thêm tiêu đề và nhạc nhỏ dưới tiếng nói.

> Tiếp tục project ca-phe-01, sửa câu cuối thành “Hẹn gặp bạn cuối tuần”, xuất bản mới.

## Chỗ để từng loại file

```text
Piu Editor/
├── AGENTS.md              AI đọc đầu tiên
├── README.md              Hướng dẫn cho bạn
├── Source/                Toàn bộ nguyên liệu gốc
│   ├── inbox/             File mới, chưa phân loại
│   ├── footage/           Video quay gốc
│   ├── images/            Ảnh gốc
│   ├── music/             Nhạc nền gốc
│   ├── audio/             Giọng đọc, lời thoại, hiệu ứng âm thanh
│   ├── assets/            Font, logo, model 3D, texture, Lottie, bộ nhận diện
│   └── documents/         Brief, kịch bản, phụ đề, transcript, tài liệu yêu cầu
├── projects/              Mỗi video một project: brief, code, working, previews, notes
├── output/                File giao cuối, chia theo project
├── temp/                  Cache và file tạm có thể tạo lại
├── repos/                 18 AGENTS.md; source tải riêng theo manifest
├── docs/                  Bản đồ và quy trình
├── configs/               Registry công cụ và provenance upstream
├── templates/             Mẫu project mới
├── scripts/               Lệnh tạo project, kiểm tra và lập danh sách nguyên liệu
└── .workspace/            Bản lưu metadata Git cũ, chỉ có trên máy này
```

`Source` viết hoa được giữ từ thư mục sẵn có. Trên Windows, `Source` và `source` là cùng một tên; mã dựng nằm ở `projects/<id>/src` để tránh nhầm với nguyên liệu.

Inventory quét toàn bộ `Source/`, kể cả thư mục con do bạn tự tạo. Các file thả trực tiếp vào `Source/` vẫn được nhận diện. Biết loại file thì bỏ thẳng vào thư mục tương ứng; `Source/inbox/` chỉ dành cho file chưa phân loại. Khi clone, các nhóm nguyên liệu chỉ chứa placeholder; người dùng hoặc AI bổ sung file sau.

`Source/images/` là ảnh đầu vào, không dành riêng cho ảnh AI. Ảnh AI tạo mới và các bản chỉnh sửa phục vụ một video được lưu ở `projects/<id>/working/generated/` hoặc thư mục working tương ứng, giúp tách nguyên liệu gốc khỏi kết quả xử lý.

Hướng dẫn AI được giữ gọn: một `AGENTS.md` ở gốc, một file cho mỗi repo công cụ, một file chung trong `Source/` và một file chung trong `projects/`. Các thư mục ảnh/nhạc/video và project mới không tự có AGENTS riêng; chỉ thêm khi có quy tắc đặc thù.

## Các lệnh tiện ích

Chạy từ gốc workspace, cần Python 3.10 trở lên và không cần cài package Python:

```powershell
python scripts/studio.py doctor
python scripts/studio.py new ca-phe-01 --title "Quảng cáo quán cà phê"
python scripts/studio.py inventory --project ca-phe-01 --hash
python scripts/studio.py validate
```

- `doctor`: kiểm tra công cụ hiện có, không tự cài phần mềm.
- `new`: tạo khung hồ sơ dự án, không render và không chép nguyên liệu.
- `inventory`: cập nhật danh sách file, giữ lựa chọn asset cũ, có thể tính hash để nhận diện bản gốc.
- `validate`: kiểm tra cấu trúc, bản đồ, 18 hướng dẫn và dữ liệu project, không cần nguyên liệu hoặc source đã tải. Thêm `--sources` để yêu cầu file source, `--local` để yêu cầu nguyên liệu đã chọn và output lịch sử.

Những lệnh này chuẩn bị và quản lý dự án. AI vẫn cần cài đúng công cụ cho từng video, viết lệnh dựng hoặc composition, rồi kiểm tra bản xuất thật.

## Đọc tiếp

- [Bản đồ dùng repo nào](docs/REPO-MAP.md)
- [Quy trình dựng video](docs/WORKFLOW.md)
- [Kho kinh nghiệm sản xuất và bài học từ TVC Yên Thành](docs/production/README.md)
- [Cách bổ sung công cụ và quản lý Git](docs/EXTENDING.md)
- [Clone, tải source và phạm vi đưa lên Git](docs/GIT.md)
- [Cách đóng góp và kiểm tra thay đổi](CONTRIBUTING.md)
- [Lịch sử phát triển](CHANGELOG.md)
- [Cách AI kiểm tra và cập nhật công cụ](docs/UPDATING.md)
- [Đánh giá chi tiết 18 repo](DANH-GIA-18-REPO.md)

Workspace có một Git repo ở gốc. Chỉ hướng dẫn local của 18 công cụ được theo dõi; source tải về nằm trên máy và không có `.git` lồng trong `repos/`. Media đầu vào, bản xuất, font, cache và metadata lưu trữ bị ignore; thư mục giữ bằng `.gitkeep`. AI vẫn đọc được file local, nhưng clone repo không mang theo chúng. Code và hồ sơ của ca TVC được giữ để học lại; media cần được lưu trữ riêng.

Khi cần bảo trì, bạn có thể nói: “Kiểm tra Remotion và GSAP, cập nhật nếu có lợi cho việc dựng video; giữ hướng dẫn riêng, sao lưu và kiểm tra tương thích.” AI được hướng dẫn đọc quy trình cập nhật trước khi làm. Đây là hướng dẫn thao tác; chưa có lệnh tự động nâng cả bộ.
