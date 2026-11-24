# 04 — Kiến trúc logic và quy ước giao tiếp module

## 1. Tại sao phải tách module?

Nhóm có 5 người: nếu mỗi người lập trình một kiểu dữ liệu riêng thì ghép hệ thống sẽ tốn nhiều công sức hơn viết code. Cần thống nhất **đầu vào, đầu ra và cách xử lý lỗi** trước khi code.

Luồng chính:

**CLI → Data Loader → Preprocessing → (Rule Engine + Statistics Engine) → Classifier → Result/Reporting**.  
**Evaluation** gọi Classifier trên dữ liệu có nhãn và tính metrics.

## 2. Thành phần và người phụ trách

| Thành phần | Trách nhiệm | Người dự kiến |
|---|---|---|
| Data Loader | Đọc email, CSV/TXT, kiểm tra dữ liệu | TV1 |
| Preprocessing | Chuẩn hóa và tokenize | TV1 |
| Rule Engine | Tính điểm theo cấu hình luật | TV2 |
| Statistics Engine | Tạo bảng trọng số, tính S_stat | TV3 |
| Classifier | Kết hợp điểm, chọn ngưỡng, trả kết quả | TV4 |
| Console CLI | Menu, nhập/xuất và thông báo | TV4 |
| Evaluation/Reporting | Metric, so sánh, xuất báo cáo | TV5 |

## 3. Định dạng dữ liệu chuẩn

**Email:** `email_id` (chuỗi), `subject` (chuỗi), `body` (chuỗi), `label` (`spam`/`ham`/trống). `source_group` có thể có trong file dữ liệu nhưng không tham gia phân loại.

**Dữ liệu tiền xử lý:** danh sách token chữ thường, ranh giới từ rõ ràng. Một quy trình dùng cho Rule Engine (giữ stopwords) và một tập token riêng cho thống kê (có thể loại stopwords), đều xuất phát từ cùng nguyên tắc chuẩn hóa.

**Kết quả phân loại:**

| Trường | Ví dụ | Ý nghĩa |
|---|---|---|
| `email_id` | E0001 | Định danh |
| `prediction` | spam | Nhãn dự đoán |
| `mode` | combined | Chế độ |
| `rule_score` | 3.0 | Điểm luật |
| `stat_score` | 1.4 | Điểm thống kê |
| `total_score` | 4.4 | Điểm được sử dụng khi combined |
| `threshold` | 1.0 | Ngưỡng tương ứng với chế độ |
| `matched_rules` | Danh sách | Luật khớp và trọng số |
| `top_keywords` | Danh sách | Token và W có ảnh hưởng |

Khi chạy `rule_only` hoặc `statistics_only`, trường `total_score` nên chứa **điểm thực sự dùng để so ngưỡng trong chế độ đó**; `rule_score` và `stat_score` vẫn có thể được trình bày để giải thích. Cần chốt chính xác quy ước này khi triển khai API nội bộ.

## 4. Interface chức năng dự kiến

| Chức năng | Đầu vào | Đầu ra |
|---|---|---|
| `load_emails` | Đường dẫn TXT/CSV | Danh sách Email hợp lệ hoặc lỗi có giải thích |
| `tokenize` | Văn bản | Danh sách token chuẩn hóa |
| `filter_stat_tokens` | Danh sách token | Token dùng cho thống kê |
| `score_rules` | Token đủ stopwords, tập luật | `rule_score`, `matched_rules` |
| `train_statistics` | Train emails có nhãn | Keyword model (đã có từ/df/weights) |
| `score_statistics` | Token thống kê, model | `stat_score`, `top_keywords` |
| `classify_email` | Email, mode, model, settings | Kết quả phân loại chuẩn |
| `evaluate` | Nhãn thật + nhãn dự đoán | Confusion matrix và metrics |
| `export_results` | Nhiều kết quả + đường dẫn | CSV/JSON báo cáo |

Chữ ký hàm cụ thể và cấu trúc lỗi cần được ghi thống nhất trong `docs/interface_contract.md` **trước khi code**. Không để TV2 hoặc TV3 tự đổi kiểu kết quả mà không thông báo TV4/TV5.

## 5. Quy tắc xử lý lỗi

- File không tồn tại, file rỗng, CSV thiếu cột, nhãn sai: báo lý do rõ ràng.
- JSON cấu hình lỗi: chỉ ra cấu hình nào sai, không tiếp tục với dữ liệu không nhất quán.
- Chưa có bảng trọng số: hướng dẫn người dùng chạy menu tạo thống kê.
- Nội dung email trống: yêu cầu nhập lại, không tạo dự đoán giả.
- Lỗi xử lý từng hàng CSV: ghi nhận hàng lỗi, không làm mất tất cả kết quả hợp lệ (quy định số hàng thành công/thất bại).
- Kết quả phải tái lập; nếu có thứ tự bằng nhau khi chọn từ khóa, sắp xếp phụ theo thứ tự từ vựng.

## 6. Cấu trúc repository tham khảo

    email-spam-filter/
    ├── data/                   # raw/ (không public), processed/, train/val/test
    ├── src/
    │   ├── data_loader.py
    │   ├── preprocessing.py
    │   ├── rules.py
    │   ├── statistics.py
    │   ├── classifier.py
    │   ├── evaluation.py
    │   └── reporting.py
    ├── config/                 # rules.json, settings.json
    ├── tests/
    ├── docs/
    ├── outputs/
    ├── main.py
    ├── README.md
    └── .gitignore

