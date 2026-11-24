# 03 — Dữ liệu và đánh giá kết quả

## 1. Dữ liệu được lấy ở đâu?

**Đề xuất:** Apache SpamAssassin Public Corpus, nguồn: https://spamassassin.apache.org/old/publiccorpus/ . Trang README gốc: https://spamassassin.apache.org/old/publiccorpus/readme.html . Bộ corpus mô tả các nhóm `spam`, `easy_ham`, `hard_ham`, `spam_2`, `easy_ham_2`, tổng cộng **6.047 email** (dữ liệu lịch sử).

Nhóm bắt đầu từ `spam` và `easy_ham` để đảm bảo dễ triển khai. Chỉ dùng **một phần 500 email hợp lệ**, mục tiêu **250 Spam + 250 Ham**; chưa có dữ liệu thực tế trong bộ tài liệu này. Chọn từ mẫu sau khi loại bản ghi lỗi và trùng.

**Tại sao không chọn UCI Spambase làm chính?** UCI Spambase cung cấp đặc trưng thống kê sẵn (4.601 email, 57 features), phù hợp huấn luyện/đánh giá phân loại dựa trên feature, nhưng không tiện nếu bài tập yêu cầu nhóm tự đọc và tách từ trên nội dung email gốc. Nguồn: https://archive.ics.uci.edu/dataset/94/spambase .

## 2. Cách chuẩn hóa dữ liệu

Dữ liệu sau khi trích xuất nên có các cột:

| Cột | Nội dung | Ví dụ |
|---|---|---|
| `email_id` | ID duy nhất | E0001 |
| `subject` | Tiêu đề | Weekly meeting |
| `body` | Nội dung văn bản thuần | Please see the agenda. |
| `label` | Nhãn gốc | ham |
| `source_group` | Nhóm nguồn để truy vết | easy_ham |

**Quan trọng:** `label` và `source_group` chỉ dùng để tổ chức/đánh giá, **không đưa vào văn bản để classifier học**. Không sử dụng header hoặc tên file vốn có thể tiết lộ nhãn, như `X-Spam-Status`, `X-Spam-Flag` hoặc đường dẫn thư mục `spam/ham`.

Với email MIME: trích `text/plain` trước; nếu chỉ có HTML thì lấy phần văn bản (không chạy script). Bỏ qua attachment. Các email không đọc được, trống hoặc nhãn lỗi phải được đếm và ghi trong biên bản xử lý.

## 3. Chia dữ liệu Train, Validation, Test

| Tập | Số lượng mục tiêu | Được sử dụng để |
|---|---:|---|
| Train | 350 email | Đếm từ khóa, ước lượng trọng số; thiết kế luật ban đầu |
| Validation | 75 email | Thử và chọn ngưỡng, kiểm tra thay đổi trước khi chốt |
| Test | 75 email | Đánh giá cuối cùng độc lập |
| **Tổng** | **500 email** | |

Chia theo nhãn gần cân bằng và cố định random seed **42**. Ví dụ Train có 175 Spam + 175 Ham; Validation 38 Spam + 37 Ham; Test 37 Spam + 38 Ham. Cần loại trùng (dựa trên nội dung chuẩn hóa) **trước** khi chia, đồng thời kiểm tra không có bản ghi trùng giữa các tập.

### Data leakage là gì?

Là khi thông tin đáng lẽ chỉ dùng để đánh giá vô tình lọt vào bước xây dựng hoặc điều chỉnh thuật toán. Ví dụ:

- Từ khóa được đếm trên **toàn bộ 500 email**, bao gồm test → không hợp lệ.
- Lấy chữ `spam` từ tên thư mục rồi dùng làm feature → không hợp lệ.
- Xem kết quả test để sửa ngưỡng, sau đó báo test đã tốt → đánh giá lạc quan.
- Cùng nội dung email xuất hiện ở train và test → kết quả có thể bị thổi phồng.

## 4. Đánh giá là gì?

**Spam là lớp dương** trong mọi công thức, phải ghi rõ điều này trong báo cáo.

| Tên | Ý nghĩa |
|---|---|
| TP | Spam thật, dự đoán Spam |
| TN | Ham thật, dự đoán Ham |
| FP | Ham thật, nhưng dự đoán Spam |
| FN | Spam thật, nhưng dự đoán Ham |

**Công thức:**

- `Accuracy = (TP + TN)/(TP + TN + FP + FN)`
- `Precision = TP/(TP + FP)`
- `Recall = TP/(TP + FN)`
- `F1 = 2 × Precision × Recall/(Precision + Recall)`
- `FPR = FP/(FP + TN)`

Nếu mẫu số bằng 0, kết quả phải được xử lý có quy ước, không để chương trình lỗi (ví dụ trả về 0 và có chú thích rằng metric không xác định trong trường hợp này).

## 5. Ví dụ tính metric

Giả sử tập test 75 email có: `TP=32`, `TN=34`, `FP=3`, `FN=6`.

- Accuracy = (32+34)/75 = **88.0%**.
- Precision = 32/(32+3) ≈ **91.4%**.
- Recall = 32/(32+6) ≈ **84.2%**.
- F1 ≈ **87.7%**.
- FPR = 3/(3+34) ≈ **8.1%**.

**Đây là số giả định để học cách tính, không phải kết quả dự án.**

## 6. Ba phép thử bắt buộc

Đánh giá **Rule-only**, **Statistics-only**, **Combined** trên **chính cùng test set**. Với mỗi chế độ, báo cáo TP/TN/FP/FN, Accuracy, Precision, Recall, F1, FPR và ngưỡng đã chọn trên validation. Nên bổ sung baseline luôn đoán lớp phổ biến nhất để có mốc tham chiếu.

Điểm mục tiêu **Accuracy ≥ 80%** là kỳ vọng tham khảo, không phải yêu cầu bắt buộc nếu dữ liệu thực tế cho kết quả thấp. Giá trị học thuật quan trọng là đánh giá đúng phương pháp và giải thích nguyên nhân.

## 7. An toàn, bản quyền và cách lưu trong Git

README chính thức của SpamAssassin nhấn mạnh **không gửi email mẫu vào hệ thống mail đang hoạt động**, và **bản quyền văn bản thư vẫn thuộc người gửi ban đầu**. Vì vậy:

- Chỉ xử lý offline, tuyệt đối không thử gửi email lên hộp thư thật.
- Không đăng tải nguyên bộ corpus hoặc nội dung email cá nhân lên GitHub công khai.
- Chỉ nộp phần dữ liệu đúng yêu cầu giảng viên và được phép sử dụng; tốt nhất cung cấp script/hướng dẫn tải nguồn, metadata và mẫu tự tạo.
- Bỏ qua mã thực thi, attachment và không truy cập link đính kèm trong email.

## 8. Bàn giao cần có từ khâu dữ liệu

Một tập train/validation/test đã làm sạch; mô tả số lượng Spam/Ham; log số email bị loại; quy tắc lấy Subject/Body; xác nhận không trùng giữa các tập; script hoặc hướng dẫn tái tạo dữ liệu.
