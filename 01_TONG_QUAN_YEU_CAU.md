# 01 — Tổng quan dự án và yêu cầu sản phẩm

## 1. Bài toán là gì?

**Spam** là thư điện tử không mong muốn, thường chứa quảng cáo, lời mời nhận thưởng, nội dung đáng ngờ... **Ham** là thư bình thường. Không phải email có chữ “free” thì chắc chắn là Spam; chúng ta chỉ dự đoán từ những tín hiệu trong nội dung.

Ví dụ: email có tiêu đề **“Claim your prize”**, nội dung **“Congratulations, winner! Claim your prize today.”** có nhiều từ gợi ý Spam. Trái lại, **“Meeting agenda for Friday”** có các từ xuất hiện thường xuyên hơn ở thư thông thường trong một số tập dữ liệu.

## 2. Sản phẩm cuối cùng hoạt động như thế nào?

1. Người dùng chọn một chức năng trong **Console CLI**.
2. Chương trình đọc email (nhập tay, TXT hoặc CSV) và chuẩn hóa văn bản.
3. **Rule Engine** đối chiếu với danh sách luật và tính điểm dương/âm.
4. **Statistics Engine** tra bảng trọng số từ khóa xây dựng từ tập train.
5. **Classifier** tổng hợp điểm, so với ngưỡng và trả về `spam` hoặc `ham`.
6. CLI hiển thị điểm và lý do; kết quả hàng loạt có thể lưu CSV.
7. **Evaluation** so sánh dự đoán với nhãn thật trên tập test độc lập.

**Đầu vào:** Subject, Body; nhãn thật chỉ có khi đánh giá.  
**Đầu ra:** Nhãn dự đoán; điểm luật; điểm thống kê; điểm tổng; ngưỡng; các luật/từ khóa có ảnh hưởng.

## 3. Phạm vi bắt buộc

| Mã | Chức năng | Mức độ hoàn thành yêu cầu |
|---|---|---|
| FR-01 | Nhập email thủ công | Cho nhập Subject, Body nhiều dòng và kết thúc nhập rõ ràng |
| FR-02 | Nhập từ file TXT/CSV | Đọc file đúng định dạng và báo lỗi file không hợp lệ |
| FR-03 | Tiền xử lý văn bản | Chuẩn hóa, tách token, áp dụng quy ước dùng chung |
| FR-04 | Rule-based | Khớp từ/cụm từ, tính điểm, ghi nhận luật được kích hoạt |
| FR-05 | Keyword statistics | Đếm số thư chứa từ, tính trọng số từ train |
| FR-06 | Hybrid classifier | Rule-only, Statistics-only và Combined |
| FR-07 | Giải thích phân loại | Hiển thị điểm thành phần và bằng chứng |
| FR-08 | Xử lý theo lô | Nhận CSV, xuất CSV dự đoán |
| FR-09 | Đánh giá | Accuracy, Precision, Recall, F1, TP/TN/FP/FN |
| FR-10 | CLI menu | Giao diện menu, xử lý lỗi và thoát an toàn |
| FR-11 | Ngưỡng | Xem/chỉnh ngưỡng, lưu cấu hình |
| FR-12 | Xem từ khóa | Hiển thị danh sách từ thiên về Spam/Ham |
| FR-13 | Tạo lại thống kê | Chỉ xây dựng từ tập train |
| FR-14 | So sánh phương pháp | Đo 3 chế độ trên cùng tập test độc lập |

## 4. Menu dự kiến

| Phím | Tác vụ |
|---|---|
| 1 | Nhập và phân loại email |
| 2 | Phân loại email từ tệp TXT |
| 3 | Phân loại nhiều email từ CSV |
| 4 | Tạo/cập nhật bảng thống kê từ khóa từ tập train |
| 5 | Chạy đánh giá trên tập test có nhãn |
| 6 | Xem bảng trọng số từ khóa |
| 7 | Xem/chỉnh ngưỡng phân loại |
| 0 | Thoát |

## 5. Ngoài phạm vi (không làm ở phiên bản đầu)

- Giao diện web hoặc GUI desktop.
- Kết nối tài khoản Gmail/Outlook; đọc thư thật của cá nhân; tự gửi/xóa thư.
- Phân tích attachment, chạy mã đính kèm, truy vấn đường link, quét virus.
- Huấn luyện Naive Bayes/SVM/Deep Learning hoặc gọi AI bên ngoài.
- Hỗ trợ tiếng Việt đầy đủ; bản đầu dùng email **tiếng Anh**.
- Đảm bảo chống phishing hoặc chống thư rác trong môi trường thực tế.

## 6. Chất lượng kỳ vọng

- Python **3.11+**, chạy offline, ưu tiên Standard Library.
- Cùng dữ liệu và cấu hình phải cho cùng kết quả.
- Xử lý ít nhất 500 email trên máy tính thông thường, không có mục tiêu mili-giây cứng khi chưa benchmark.
- Không để lỗi nhập liệu khiến chương trình thoát bất ngờ; thông báo bằng tiếng Việt.
- Kiểm thử độc lập từng module và kiểm thử tích hợp.
- **Accuracy ≥ 80% là mục tiêu phấn đấu**, không phải cam kết hay điều kiện đánh trượt tự động; cần báo cáo số liệu thực nghiệm thật.
- Không báo “xác suất 90% Spam” từ điểm số tự thiết kế vì điểm này **không phải xác suất**.
