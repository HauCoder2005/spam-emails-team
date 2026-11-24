# 05 — WBS và phân công công việc cho nhóm 5 người

## 1. Mục tiêu phân công

Mỗi người phải có **module kỹ thuật riêng, test riêng, tài liệu giải thích và sản phẩm bàn giao**. Không phân công một người chỉ làm slide/báo cáo. Tên hiện được mã hóa TV1–TV5 để nhóm tự gán theo năng lực.

## 2. Sơ đồ WBS tổng quát

| WBS | Work package | Phụ trách chính | Đầu ra |
|---|---|---|---|
| 1.0 | Khởi tạo + chốt interface | TV2 điều phối; TV4 kỹ thuật | Repo, quy ước, hợp đồng dữ liệu |
| 2.0 | Data & Preprocessing | **TV1** | CSV sạch, hàm đọc/tách từ |
| 3.0 | Rule Engine & Configuration | **TV2** | Luật, điểm luật, bằng chứng khớp |
| 4.0 | Keyword Statistics | **TV3** | Bảng trọng số, điểm thống kê |
| 5.0 | Classifier & Console CLI | **TV4** | Chương trình CLI end-to-end |
| 6.0 | Evaluation & Quality Assurance | **TV5** | Metrics, so sánh, test, báo cáo |
| 7.0 | Tích hợp + demo + báo cáo | **Cả nhóm** | Bản release, README, slide/demo |

## 3. TV1 — Data & Preprocessing

**Phải làm:** thu thập dữ liệu từ nguồn, trích Subject/Body; xử lý MIME/HTML ở mức cần thiết; loại bản ghi lỗi/trùng; chọn 250 Spam/250 Ham nếu khả thi; chia train/validation/test; xây dựng chuẩn hóa văn bản và tokenizer; viết test cho dữ liệu.

**Bàn giao:** `src/data_loader.py`, `src/preprocessing.py`, `data/train.csv`, `data/validation.csv`, `data/test.csv`, `tests/test_preprocessing.py`, `docs/data_description.md`.

**Nghiệm thu:** 500 bản ghi mục tiêu nếu nguồn đáp ứng; split không giao nhau; nhãn đúng; có số liệu loại bỏ; hàm token nhất quán; có test PASS. **Phụ thuộc:** phải phát hành dữ liệu mẫu và contract sớm cho TV2–TV5.

## 4. TV2 — Rule Engine & Configuration (đồng thời điều phối)

**Phải làm:** cấu hình luật có mã/từ/cụm/trọng số; khớp theo token; tính một lần/luật/email; tổng chặn [-5,5]; ghi nhận luật khớp; kiểm tra file cấu hình; unit test. Điều phối giao việc/họp ngắn và tổng hợp báo cáo cùng TV5.

**Bàn giao:** `src/rules.py`, `config/rules.json`, `tests/test_rules.py`, `docs/rule_specification.md`.

**Nghiệm thu:** tính đúng điểm, có bằng chứng; không khớp từ con; xử lý cấu hình lỗi; không viết thuật toán trực tiếp trong CLI.

## 5. TV3 — Keyword Statistics

**Phải làm:** đếm document frequency ở train; tính xác suất làm trơn, trọng số log-ratio; lọc từ có df ≥3; chặn trọng số [-2,2]; chọn top-5 theo |W|; tính `S_stat`; lưu/tải bảng thống kê; unit test công thức.

**Bàn giao:** `src/statistics.py`, `data/processed/keyword_stats.json`, `tests/test_statistics.py`, `docs/statistics_method.md`.

**Nghiệm thu:** chỉ học train; tính đúng số; từ chưa thấy có điểm 0; chạy lại cùng dữ liệu ra kết quả như nhau.

## 6. TV4 — Classifier & Console CLI (đồng thời tích hợp kỹ thuật)

**Phải làm:** thiết kế repo và quy trình Git; điều phối Rule Engine + Statistics Engine; ba mode; áp ngưỡng đúng mode; menu 0–7; nhập nội dung/tệp; hiển thị giải thích; gọi phần Evaluation; tích hợp và sửa lỗi tương thích.

**Bàn giao:** `main.py`, `src/classifier.py`, `config/settings.json`, `tests/test_classifier.py`, `docs/cli_manual.md`.

**Nghiệm thu:** demo được CLI từ đầu tới cuối; có lỗi rõ ràng cho đầu vào sai; phân loại tay và CSV; tích hợp được module của TV1, TV2, TV3, TV5.

## 7. TV5 — Evaluation & QA

**Phải làm:** tính TP/TN/FP/FN, Accuracy/Precision/Recall/F1/FPR; so sánh 3 mode; xuất CSV/JSON; test tình huống biên; xác nhận split/no leakage; kiểm thử tích hợp; viết phần đánh giá và phối hợp báo cáo.

**Bàn giao:** `src/evaluation.py`, `src/reporting.py`, `tests/test_evaluation.py`, `tests/test_integration.py`, `outputs/evaluation_report.json`, `docs/test_report.md`.

**Nghiệm thu:** công thức và số liệu đúng; xử lý chia cho 0; so sánh cùng test; báo cáo ghi rõ dữ liệu thật và mục tiêu đặt ra.

## 8. Việc chung không thuộc riêng một người

- Cả nhóm góp ý và duyệt `interface_contract.md`.
- Mỗi người test module mình, review ít nhất một Pull Request liên quan.
- Người viết module có trách nhiệm sửa lỗi của module đó khi tích hợp.
- Cả 5 người đóng góp vào nội dung báo cáo, có thể trình bày phần mình.
- Không “đẩy” mọi lỗi sang TV4 hoặc TV5.

## 9. Tiêu chí đánh giá đóng góp nội bộ

| Tiêu chí | Tỷ trọng |
|---|---:|
| Hoàn thành tính năng được giao | 40% |
| Chất lượng code và test | 25% |
| Phối hợp và tích hợp | 15% |
| Giải thích được module và tài liệu | 10% |
| Đúng hạn, báo cáo tiến độ | 10% |

