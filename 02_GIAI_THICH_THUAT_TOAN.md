# 02 — Giải thích thuật toán (đọc hiểu và tính tay)

## 1. Một email được xử lý thế nào?

Lấy **Subject + Body** của email, rồi chuẩn hóa chữ thường, tách thành từ (token). Ví dụ:

- Subject: `WINNER!!!`
- Body: `Claim your prize now.`
- Sau chuẩn hóa: `winner claim your prize now`
- Token: `winner`, `claim`, `your`, `prize`, `now`

Đối với **Rule Engine**, cần giữ chuỗi token đầy đủ để phát hiện cụm `claim your prize` hoặc cụm nhiều từ khác mà không phá vỡ bởi stopwords. Với **Statistics Engine**, có thể loại stopwords (`your`, `the`, `is`...) theo danh sách cố định, chỉ dùng cho tính thống kê. Phương pháp tiền xử lý ở train và lúc dự đoán phải **giống nhau**.

## 2. Cách 1: Rule-based Scoring

Mỗi luật là một từ/cụm từ có điểm đã cấu hình. Ví dụ (chỉ minh họa):

| Luật | Điểm |
|---|---:|
| `winner` | +3 |
| `free` | +2 |
| `claim your prize` | +4 |
| `limited offer` | +2 |
| `meeting agenda` | -2 |

Quy tắc: từ/cụm phải khớp theo ranh giới token; mỗi luật chỉ tính **một lần trên mỗi email**; cộng tất cả điểm rồi **chặn tổng trong [-5, +5]**.

**Ví dụ:** Email chứa `winner` (+3) và `claim your prize` (+4) → tổng thô +7 → điểm luật cuối cùng **S_rule = +5** (do chặn điểm). Khi giải thích, vẫn liệt kê hai luật đã khớp.

*Lưu ý:* `win` không được khớp bừa trong `winner`. Các luật từ vựng chỉ phản ánh tín hiệu, không phải bằng chứng email chắc chắn là rác.

## 3. Cách 2: Thống kê từ khóa trong dữ liệu đã gắn nhãn

### 3.1. Đếm ở cấp độ **email**, không phải số lần từ lặp

Giả sử tập train có **175 Spam** và **175 Ham**. Từ `winner` xuất hiện trong 70 email Spam và 5 email Ham (xuất hiện 10 lần trong một email vẫn chỉ tính là **một email có từ**).

- Tỷ lệ xuất hiện đã làm trơn trong Spam: `P_s(winner) = (70+1)/(175+2) = 71/177 ≈ 0.401`.
- Tỷ lệ xuất hiện đã làm trơn trong Ham: `P_h(winner) = (5+1)/(175+2) = 6/177 ≈ 0.034`.
- Trọng số: `W(winner) = ln(P_s/P_h) = ln(71/6) ≈ 2.47`.
- Chặn trọng số vào [-2,+2] → **W(winner)=+2**.

Nếu từ xuất hiện chủ yếu trong Ham thì W âm. Nếu tỷ lệ hai lớp tương tự nhau thì W gần 0. Công thức làm trơn tránh trường hợp có lớp chưa từng xuất hiện từ khóa khiến phép log không xác định.

**Công thức tổng quát:**

`P_s(w)=(df_s(w)+1)/(N_s+2)`  
`P_h(w)=(df_h(w)+1)/(N_h+2)`  
`W(w)=clip(ln(P_s(w)/P_h(w)), -2, +2)`

Trong đó `df_s(w)` là số email Spam có từ `w`, `N_s` là tổng số email Spam trong train; tương tự với Ham.

### 3.2. Quy tắc tạo bảng từ khóa

- Chỉ dùng **train**, không học từ validation/test.
- Một từ phải xuất hiện trong ít nhất **3 email train** (tổng hai lớp) mới có trọng số trong bảng.
- Với email mới, mỗi từ chỉ tính một lần. Chọn tối đa **5 từ khóa khác nhau có |W| lớn nhất**; nếu có hòa điểm, sắp theo từ khóa tăng dần để kết quả ổn định.
- Các vị trí chưa đủ 5 từ nhận 0 điểm. `S_stat = (2/5) × tổng W_i của tối đa 5 từ`.
- Vì từng W nằm trong [-2,+2], nên S_stat thuộc [-4,+4]. Các từ ngoài bảng có trọng số 0.

**Ví dụ minh họa:** Một email có ba từ đủ điều kiện, trọng số lần lượt +2.0, +1.5 và +1.1. Khi đó `S_stat = (2/5) × (2 + 1.5 + 1.1) = 1.84`.

### 3.3. Vì sao không lấy tất cả từ xuất hiện?

Email dài có thể chứa rất nhiều từ và làm điểm tăng/giảm không kiểm soát. Giới hạn số từ ảnh hưởng lớn nhất giúp thang điểm ổn định hơn, dễ giải thích, phù hợp bài tập. Đây là lựa chọn thiết kế cần **kiểm chứng thực nghiệm**, không phải công thức chuẩn của mọi bộ lọc spam.

## 4. Kết hợp hai phương pháp

`S_total = S_rule + S_stat`

- Ban đầu đặt ngưỡng Combined `T_combined = 1.0`.
- Nếu `S_total >= T_combined` → dự đoán `spam`.
- Ngược lại → `ham`.

**Ví dụ:** `S_rule = 5`, `S_stat = 1.84` → `S_total = 6.84` → `spam` khi T=1.0.

Điểm tổng **không phải tỷ lệ phần trăm hay xác suất**. Nếu email chỉ có `meeting agenda`, điểm có thể âm và được phân loại Ham khi dưới ngưỡng.

## 5. Ba chế độ cần có

| Chế độ | Điểm dùng để phân loại | Ngưỡng |
|---|---|---|
| Rule-only | `S_rule` | `T_rule` |
| Statistics-only | `S_stat` | `T_stat` |
| Combined | `S_rule + S_stat` | `T_combined` |

Ba ngưỡng được chọn **riêng trên validation** (chỉ sau khi bảng từ khóa và luật được tạo từ train). Có thể thử một tập ngưỡng ứng viên xác định trước, chọn theo tiêu chí đánh giá nhất quán và cố định trước khi chạy test.

## 6. Thế nào là kết quả giải thích tốt?

Một kết quả trên terminal nên cho thấy:

- Nhãn: `spam` hoặc `ham`.
- Chế độ: `combined`.
- Điểm luật, điểm thống kê, điểm tổng và ngưỡng.
- Các luật khớp, điểm tương ứng.
- Tối đa 5 từ khóa thống kê có ảnh hưởng, trọng số dương/âm.

Không dùng từ “AI chắc chắn” hoặc “Spam 98%” vì hệ thống không tính xác suất đã hiệu chuẩn.

## 7. Những trường hợp thường gây sai

1. **Từ con:** `free` trong từ khác phải xử lý theo ranh giới token.
2. **Chữ hoa:** `WINNER` và `winner` cần cùng kết quả.
3. **Từ lặp:** `free free free` không kích hoạt luật 3 lần nếu luật quy định một lần.
4. **Stopwords:** Không loại stopwords trước khi kiểm tra cụm luật.
5. **Từ chưa thấy trong train:** Cho trọng số 0, không báo lỗi.
6. **Email dài:** Chỉ chọn tối đa 5 từ có |W| lớn nhất.
7. **Thay ngưỡng sau khi xem test:** Làm đánh giá test không còn độc lập.

### Tự kiểm tra sau khi đọc

- Tại sao `df_s(w)` đếm theo **số email có từ** thay vì tổng số lần từ xuất hiện?
- Với điểm luật 3.0, điểm thống kê -1.4 và ngưỡng 1.0, email được phân loại là gì? **Đáp án: Spam** vì tổng = 1.6 ≥ 1.0.
- Nếu từ khóa chỉ xuất hiện trong Ham thì trọng số nghiêng về dấu nào? **Đáp án: âm**.
