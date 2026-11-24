# Báo cáo phương pháp Thống kê từ khóa (Keyword Statistics)

- **Phụ trách:** leehuy (Thành viên 3) — Nhánh `leehuy/statistics-classification`
- **Notebook thực thi:** `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
- **Hàm lõi sử dụng:** `src/statistics.py` (`train_statistics`, `save_statistics`, `load_statistics`, `score_statistics`, `get_top_keywords_by_class`)

---

## 1. Công thức thuật toán

1. **Đếm Document Frequency theo cấp độ email (CHỈ trên `data/train.csv`):**
   - Mỗi email dùng tập từ duy nhất `set(stat_tokens)` (đã bỏ `STOPWORDS` và token dài `< 2`) để từ lặp nhiều lần trong 1 email không làm méo thống kê.
   - Lọc bỏ từ hiếm: chỉ giữ các từ xuất hiện trong ít nhất `min_df = 3` email (`df_spam[w] + df_ham[w] >= 3`).
2. **Làm trơn Laplace & trọng số log-ratio:**
   $$P_s(w) = \frac{df_s(w) + 1}{N_s + 2}, \qquad P_h(w) = \frac{df_h(w) + 1}{N_h + 2}, \qquad W(w) = \text{clip}\left(\ln\frac{P_s(w)}{P_h(w)}, -2.0, +2.0\right)$$
3. **Chấm điểm email mới (`score_statistics`):**
   - Từ chưa thấy trong tập train nhận trọng số `0` (bỏ qua, không lỗi — T05).
   - Chọn tối đa **Top-5 từ khác nhau có `|W|` lớn nhất**; nếu hòa điểm thì sắp xếp phụ tăng dần theo bảng chữ cái `(-abs(w), token)` để đảm bảo kết quả tái lập 100% (T11).
   - Công thức điểm thống kê (nằm trong `[-4.0, +4.0]`):
     $$S_{\text{stat}} = \frac{2}{5} \sum_{i=1}^{k} W_i \quad (k \le 5)$$

> **Lưu ý học thuật:** `S_stat` là điểm phân loại dựa trên trọng số từ khóa, không phải xác suất `% Spam`.

---

## 2. Kết quả thực nghiệm trên tập dữ liệu thật

### 2.1. Thống kê bảng trọng số (`data/processed/keyword_stats.json`)
- **Tập huấn luyện:** `data/train.csv` (`N_spam = 175`, `N_ham = 175`, tổng 350 email, 0 data leakage).
- **Ngưỡng lọc tần suất:** `min_df = 3`.
- **Kích thước từ vựng đạt ngưỡng:** **1.876 từ**
  - Từ thiên về Spam (`W > 0`): **891 từ**
  - Từ thiên về Ham (`W < 0`): **891 từ**
  - Từ trung tính (`W = 0`): **94 từ**

### 2.2. Kiểm chứng công thức & tình huống biên
- Ví dụ tính tay `(2/5) * (2.0 + 1.5 + 1.1) = 1.84`: **PASS**
- Từ chưa thấy trong train (`T05`): **PASS**
- Hòa điểm `|W|` sắp xếp ổn định theo alphabet (`T11`): **PASS**
- Từ lặp trong 1 email chỉ tính 1 lần & tính tái lập (`T14`): **PASS**

### 2.3. Phân bố điểm `S_stat` trên tập Validation (75 email)
| Lớp thật | Số lượng | Mean `S_stat` | Median `S_stat` | Min | Max |
|---|---:|---:|---:|---:|---:|
| `spam` | 38 | `+2.0319` | `+2.4000` | `-2.0805` | `+4.0000` |
| `ham` | 37 | `-3.3511` | `-4.0000` | `-4.0000` | `+2.1306` |

→ Điểm `S_stat` phân tách rất rõ giữa email `spam` (trung vị `+2.40`) và email `ham` (trung vị `-4.00`).

---

## 3. Đầu ra bàn giao
- `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
- `data/processed/keyword_stats.json` (tái tạo cục bộ từ `train.csv`)
- `outputs/stat_val_scores.csv` (75 dòng, 5 cột chuẩn)
- `outputs/stat_test_scores.csv` (75 dòng, 5 cột chuẩn)
- `outputs/figures/stat_top_keywords.png`
- `outputs/figures/stat_score_distribution.png`
