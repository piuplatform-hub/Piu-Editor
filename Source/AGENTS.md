# Toàn bộ nguyên liệu gốc

Áp dụng [AGENTS gốc](../AGENTS.md) và [workflow](../docs/WORKFLOW.md).

Đây là nơi duy nhất chứa nguyên liệu đầu vào dùng chung. Tất cả đường dẫn bên dưới tính từ gốc workspace:

- [Source/inbox](inbox/): file mới chưa phân loại; vẫn dùng được tại chỗ, không bắt buộc di chuyển trước khi dựng.
- [Source/footage](footage/): video quay gốc; kiểm tra ffprobe, rotation, FPS, thời lượng, hình và tiếng liên quan.
- [Source/images](images/): ảnh đầu vào; xem ảnh thật, kiểm tra orientation, độ phân giải, crop và nội dung.
- [Source/music](music/): nhạc nền; kiểm tra thời lượng, âm lượng và thông tin credit/quyền sử dụng được cung cấp.
- [Source/audio](audio/): giọng đọc, lời thoại, SFX; kiểm tra nội dung, timing và clipping. Có thể chia voiceover/dialogue/sfx.
- [Source/assets](assets/): font, logo, model, texture/HDRI, Lottie, nhận diện; chờ tải xong khi render và kiểm tra font tiếng Việt.
- [Source/documents](documents/): yêu cầu, kịch bản, transcript, phụ đề và tài liệu tham khảo; giữ nguyên tài liệu gốc, ghi brief làm việc trong project.

Một guide này áp dụng cho toàn bộ các thư mục trên; không tạo thêm AGENTS cho mỗi loại media. Chỉ bổ sung guide con khi có quy tắc đặc thù chưa thể diễn đạt ở đây.

Có thể tạo thư mục con theo dự án hoặc đợt quay. Inventory mặc định quét đệ quy toàn bộ `Source/`, bỏ qua `AGENTS.md`, `.gitkeep` và file ẩn. File được thả trực tiếp vào Source vẫn được tìm thấy. Khi biết loại file, người dùng có thể đưa thẳng vào thư mục tương ứng; inbox chỉ dành cho file chưa muốn phân loại.

Hãy nhận diện và xem nội dung trước khi chọn. Không tự di chuyển/đổi tên file để phân loại nếu người dùng chưa yêu cầu; dùng manifest của project để chọn nguyên liệu. File gốc giữ nguyên, bản dẫn xuất nằm trong project working/previews và bản giao nằm trong output.

Ảnh AI tạo mới cho một dự án và các bản resize/convert/tách nền nằm ở `projects/<id>/working/generated/` hoặc khu vực working tương ứng. `Source/images/` chứa ảnh đầu vào để dựng, không phải thư mục dành riêng cho ảnh AI. Ảnh do người dùng đưa vào có thể có nguồn gốc bất kỳ; ghi nguồn khi biết.

Thay đổi cấu trúc ngày 03/11/2026: các thư mục đầu vào ở gốc chuyển vào Source, `input` đổi thành `documents`; 7 ảnh có sẵn hiện nằm trong `Source/images/` sau khi điều chỉnh phân loại. Không tạo lại các thư mục đầu vào cũ ở gốc.
