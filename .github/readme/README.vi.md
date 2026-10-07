<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>Không có thời gian xem YouTube? Đọc bản tóm tắt nắm trọn nội dung.</strong>
</p>
<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="日本語" aria-label="日本語">🇯🇵</a> ·
  <a href="README.en.md" title="English" aria-label="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文" aria-label="简体中文">🇨🇳</a> ·
  <a href="README.ko.md" title="한국어" aria-label="한국어">🇰🇷</a> ·
  <a href="README.es.md" title="Español" aria-label="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <strong title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</strong>
</p>

busy-tube là một plugin cho Claude Code, tổng hợp các video mới từ những kênh YouTube bạn đã đăng ký thành bản tóm tắt Markdown. Công cụ dành cho những ai muốn cập nhật thông tin nhưng không có thời gian xem video.

- **Tóm tắt dựa trên nội dung thực của video.** Gemini phân tích âm thanh và hình ảnh trên màn hình, hoặc Whisper chép lời, hoặc dùng phụ đề có sẵn. Video không có phụ đề cũng được hỗ trợ.
- **Hoàn toàn miễn phí.** Không dùng API trả phí nào. Các engine trên đám mây chạy trong hạn mức miễn phí, còn engine cục bộ thì không cần cả khóa API.
- **Chỉ tóm tắt video mới.** Video đã tóm tắt sẽ được ghi lại và bỏ qua ở những lần chạy sau.
- **Tạo cả trang dễ đọc.** Xuất bản một trang có ảnh thu nhỏ, sơ đồ cơ chế hoạt động và liên kết mốc thời gian phát ngay từ cảnh tương ứng (khi có thể dùng công cụ Artifact).
- **Chọn được ngôn ngữ tóm tắt.** Mặc định là tiếng Nhật, có thể đổi bằng `config --lang`.

## Cài đặt

Cần có [uv](https://docs.astral.sh/uv/) và Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Cách dùng

Chỉ cần nhờ Claude bằng lời bình thường. Bạn cũng có thể gọi bằng lệnh gạch chéo `/busy-tube:busy-tube`.

- "Thêm https://www.youtube.com/@GoogleDevelopers vào busy-tube"
- "Tóm tắt các video YouTube mới giúp mình"
- "Viết tóm tắt bằng tiếng Anh" "Chỉ dùng whisper và phụ đề thôi"

Bản tóm tắt được hiển thị trong cuộc trò chuyện và đồng thời lưu vào `~/.busy-tube/digests/YYYY-MM-DD.md`.

Nếu công cụ Artifact khả dụng trong Claude Code (khi đã liên kết với claude.ai), bản tóm tắt cũng được xuất bản thành một trang web riêng tư chỉ bạn xem được. Trang gồm ảnh thu nhỏ, sơ đồ minh họa cơ chế cốt lõi của video và liên kết mốc thời gian phát ngay từ cảnh tương ứng.

## engine (cách lấy nội dung)

Các engine được thử theo thứ tự đã thiết lập. Engine chưa được chuẩn bị sẽ bị bỏ qua, và nếu một engine thất bại (chẳng hạn do chạm giới hạn hạn mức miễn phí) thì sẽ chuyển sang engine tiếp theo. Thứ tự mặc định là `gemini → groq → mlx-whisper → whisper → captions`.

| engine | Chuẩn bị | Điểm mạnh | Hạn chế |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([khóa miễn phí](https://aistudio.google.com/apikey)) | Nhận diện được cả slide, mã nguồn và chữ trên màn hình | Hạn mức miễn phí khoảng 20 yêu cầu/ngày, tổng thời lượng video tối đa 8 giờ/ngày, chỉ video công khai, dữ liệu đầu vào được Google dùng để cải thiện sản phẩm |
| `groq` | `export GROQ_API_KEY=...` ([khóa miễn phí](https://console.groq.com/keys)) và ffmpeg | Rất nhanh với Whisper large-v3 | Tối đa 8 giờ âm thanh mỗi ngày |
| `mlx-whisper` | Máy Mac chip Apple Silicon và ffmpeg | Chạy cục bộ, nhanh. Không cần khóa | Chỉ dành cho Mac |
| `whisper` | Không cần chuẩn bị (faster-whisper) | Chạy cục bộ. Không cần khóa. Chạy được trên mọi hệ điều hành | Khá chậm. Lần đầu sẽ tải mô hình khoảng 3GB |
| `captions` | Không cần chuẩn bị | Xong gần như tức thì | Chỉ với video có phụ đề |

Kiểm tra engine nào dùng được bằng `uv run skills/busy-tube/scripts/busy_tube.py doctor`.

Với những video chỉ có nhạc nền chẳng hạn, bản chép lời có thể là chuỗi ký tự vô nghĩa. Khi đó busy-tube sẽ tự động nhận biết và chuyển sang engine tiếp theo. Video thất bại ở mọi engine sẽ không bị đánh dấu là đã xem, nên lần sau sẽ được thử lại.

## Thiết lập

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` là số video mới tối đa lấy về cho mỗi kênh trong một lần chạy. Dữ liệu được lưu trong `~/.busy-tube/`. Nếu muốn đổi vị trí lưu, hãy đặt `BUSY_TUBE_HOME`.

## Bảo mật

Tiêu đề, mô tả và phụ đề video đều do người khác viết, nên có thể lẫn những chỉ thị độc hại nhắm vào AI. busy-tube phòng tránh điều này bằng ba cách:

- Chỉ có một agent tóm tắt chuyên dụng, vốn chỉ có quyền đọc file, mới đọc nội dung video.
- Nội dung được bọc trong dấu hiệu "nội dung không đáng tin cậy" trước khi chuyển đi.
- Trên trang được xuất bản, toàn bộ văn bản đều được làm sạch và mọi liên kết không thuộc YouTube đều bị loại bỏ.

Khóa API chỉ được đọc từ biến môi trường và không bao giờ được lưu vào file.

## Phát triển

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # kiểm thử đơn vị (không phụ thuộc)
claude --plugin-dir .                                # chạy thử cục bộ
```

## Giấy phép

MIT
