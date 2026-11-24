# 06 — Quy trình cộng tác, tiến độ và nghiệm thu

## 1. Quy trình Git tối giản

**Repo:** `email-spam-filter` (tên đề xuất) với nhánh ổn định `main`.

| Thành viên | Nhánh làm việc |
|---|---|
| TV1 | `feature/data-preprocessing` |
| TV2 | `feature/rule-engine` |
| TV3 | `feature/keyword-statistics` |
| TV4 | `feature/classifier-cli` |
| TV5 | `feature/evaluation-qa` |

Quy trình: lấy code mới nhất → sửa trên nhánh cá nhân → chạy test của mình → commit rõ nội dung → tạo Pull Request → thành viên liên quan review → TV4 phối hợp merge → TV5 chạy kiểm thử tích hợp. Không trực tiếp đẩy code chưa kiểm thử lên `main`.

Không đẩy corpus thư điện tử gốc, dữ liệu riêng tư, tệp sinh tự động dung lượng lớn, hoặc tệp cấu hình chứa thông tin nhạy cảm lên repo công khai. Kiểm tra `.gitignore` từ ngày đầu.

## 2. Timeline minh họa 14 ngày

| Thời gian | Mục tiêu chính | Mốc |
|---|---|---|
| Ngày 1–2 | Chốt yêu cầu, repo, interface, dữ liệu mẫu | **M0** |
| Ngày 3–6 | Mỗi người hoàn thành bản chạy thử + unit test | **M1** |
| Ngày 7–9 | Tích hợp menu và các module, kiểm thử luồng | **M2** |
| Ngày 10–11 | Chọn ngưỡng trên validation, đánh giá test | **M3** |
| Ngày 12–14 | Sửa lỗi, README, báo cáo, demo | **M4** |

**Lưu ý:** 14 ngày chỉ là phương án đề xuất, chưa có ngày nộp chính thức. Nếu cần rút ngắn, ưu tiên hoàn thành logic và test, không bỏ bước tránh leakage để làm đẹp slide.

## 3. Phụ thuộc và cách làm song song

TV1 phát hành **tập 10–20 email mẫu tự tạo và định dạng chung** sớm, không chờ đủ 500 email. TV2 viết luật và unit test trên mẫu; TV3 kiểm tra công thức thống kê trên mẫu có nhãn; TV4 tạo CLI giả lập kết quả đúng interface; TV5 làm công thức metric trên nhãn giả định. Khi các thành phần sẵn sàng, thay mẫu bằng bộ xử lý thật và chạy tích hợp.

**Điểm chặn quan trọng:** Không nên code hàng loạt trước khi chốt các trường Email, Result, chức năng `tokenize`, dạng trả kết quả từ Rule Engine và Statistics Engine.

## 4. Kiểm thử tối thiểu

| Test | Tình huống | Kết quả mong đợi |
|---|---|---|
| T01 | `WINNER` vs `winner` | Quy tắc thống nhất |
| T02 | `free` trong từ khác | Không khớp nhầm |
| T03 | Từ/cụm lặp | Không nhân đôi điểm ngoài quy tắc |
| T04 | Email có tín hiệu Spam và Ham | Cộng điểm dương/âm đúng |
| T05 | Từ chưa thấy trong train | Trọng số 0 |
| T06 | Email rỗng | Báo lỗi rõ ràng |
| T07 | TXT không tồn tại | Xử lý lỗi, quay về menu |
| T08 | CSV thiếu cột bắt buộc | Báo cấu trúc lỗi |
| T09 | JSON luật sai | Không âm thầm dùng luật lỗi |
| T10 | Chưa tạo model thống kê | Hướng dẫn tạo model |
| T11 | Chọn top-5 có điểm bằng nhau | Kết quả ổn định |
| T12 | Metric với mẫu số 0 | Không crash, có quy ước |
| T13 | Trùng email xuyên các tập | Bị phát hiện hoặc chặn |
| T14 | Cùng dữ liệu và cấu hình | Chạy lại ra cùng kết quả |
| T15 | Chạy cả ba chế độ cùng test | Báo cáo có thể so sánh |

## 5. Definition of Done — Checklist nghiệm thu

- [ ] CLI chạy được trên Python 3.11+ và máy khác theo README.
- [ ] Có đủ nhập tay, TXT, CSV và xuất CSV.
- [ ] Có xử lý rỗng, file lỗi, cấu hình lỗi.
- [ ] Rule-only hoạt động và giải thích được luật khớp.
- [ ] Statistics-only hoạt động và bảng từ khóa xây dựng chỉ từ train.
- [ ] Combined hoạt động, ngưỡng được lấy từ validation.
- [ ] Không trùng train/validation/test sau chuẩn hóa.
- [ ] Có Accuracy/Precision/Recall/F1/FPR, confusion matrix.
- [ ] Có so sánh 3 chế độ trên cùng test và baseline đơn giản.
- [ ] Các test chức năng quan trọng PASS hoặc có lỗi tồn đọng được mô tả.
- [ ] Có báo cáo phương pháp, giới hạn, số liệu thực tế và nguồn dữ liệu.
- [ ] Từng thành viên giải thích được phần việc của mình trong buổi demo.
