# Giao nhiệm vụ 03 — leehuy (Phân loại bằng Thống kê từ khóa — `.ipynb`)

- **Phụ trách:** **leehuy** (Thành viên 3)
- **Nhánh Git:** `feature/statistics-classification`
- **File Notebook chính:** `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
- **Tài liệu bắt buộc đọc trước:** `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- **File bạn sở hữu (chỉ tạo/sửa các file này):**
  - `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
  - `data/processed/keyword_stats.json`
  - `outputs/stat_val_scores.csv`, `outputs/stat_test_scores.csv`
  - `outputs/figures/stat_*.png`
  - `docs/statistics_method.md`

---

## 1. Dataset Setup — Required Before Starting Tasks

Trước khi bắt đầu làm task, chạy lệnh sau để tự động khởi tạo hoặc xác thực đầy đủ bộ dữ liệu trên máy bạn:

```bash
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/setup_data.py --verify
```

- **Tập Train (DUY NHẤT dùng để tính trọng số từ khóa):** `data/train.csv` (350 email: 175 `spam` / 175 `ham`, 7 cột chuẩn).
- **Tập Validation & Test (chỉ dùng để chấm điểm `S_stat`):** `data/validation.csv` (75 email), `data/test.csv` (75 email).
- **Cột văn bản bạn sử dụng:** cột **`stat_text`** (đã chuẩn hóa chữ thường, loại `STOPWORDS` và token dài `< 2`).
- **QUY TẮC CHỐNG DATA LEAKAGE:** Tuyệt đối chỉ học bảng trọng số từ `data/train.csv`, không bao giờ tính `df` trên `validation.csv` hay `test.csv`.

---

## 2. Cấu trúc chi tiết từng phần trong `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`

1. **Huấn luyện bảng trọng số từ khóa từ `data/train.csv`:**
   - Đếm **document frequency** theo cấp độ **email** (dùng `set(stat_text.split())`, 1 từ xuất hiện 10 lần trong cùng 1 email vẫn chỉ tính là 1 email có từ đó): `df_spam[w]` và `df_ham[w]`.
   - Lọc bỏ từ hiếm: chỉ giữ từ có `df_spam[w] + df_ham[w] >= 3`.
   - Công thức làm trơn Laplace & trọng số log-ratio:
     - $P_s(w) = \frac{df_s(w) + 1}{N_s + 2}$
     - $P_h(w) = \frac{df_h(w) + 1}{N_h + 2}$
     - $W(w) = \text{clip}\left(\ln\frac{P_s(w)}{P_h(w)}, -2.0, +2.0\right)$
   - Lưu bảng trọng số ra `data/processed/keyword_stats.json` (UTF-8, gồm `version`, `min_df`, `n_spam`, `n_ham`, `vocab_size`, `weights`, `df_spam`, `df_ham`).

2. **Trực quan hóa từ khóa đặc trưng:**
   - Vẽ biểu đồ cột ngang **Top 15 từ khóa thiên về Spam (`W > 0`)** và **Top 15 từ khóa thiên về Ham (`W < 0`)**, lưu vào `outputs/figures/stat_top_keywords.png`.

3. **Cài đặt chấm điểm thống kê (`score_statistics`):**
   - Với mỗi email mới: lấy tập từ duy nhất trong `stat_text`, bỏ qua từ chưa thấy trong bảng (trọng số `0`, không lỗi — T05).
   - Chọn tối đa **top 5 từ có `|W|` lớn nhất**; nếu hòa điểm thì sắp xếp phụ theo thứ tự bảng chữ cái `key=lambda x: (-abs(x[1]), x[0])` để kết quả tái lập 100% (T11).
   - Tính điểm: $S_{\text{stat}} = \frac{2}{5} \sum_{i} W_i \in [-4.0, +4.0]$.

4. **Kiểm chứng công thức bằng `assert` ngay trong Notebook:**
   - Test ví dụ tính tay trong `02_GIAI_THICH_THUAT_TOAN.md`: 3 từ `+2.0, +1.5, +1.1` → `S_stat == 1.84`.
   - Test T05 (từ lạ), T11 (tie-break top-5), đếm theo email không bị ảnh hưởng bởi từ lặp.

5. **Chấm điểm trên `validation.csv` & `test.csv`, vẽ biểu đồ & xuất file:**
   - Vẽ biểu đồ phân bố `stat_score` của Spam vs Ham trên tập `validation` (`outputs/figures/stat_score_distribution.png`).
   - Xuất đúng 2 file CSV chuẩn 5 cột `email_id,label,label_num,stat_score,top_keywords`:
     - `outputs/stat_val_scores.csv`
     - `outputs/stat_test_scores.csv`

---

## 3. Cách chạy & Kiểm tra

```powershell
pip install -r requirements.txt
jupyter notebook notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb
```

---

## 4. Prompt chuẩn để giao cho AI Agent

Copy nguyên văn gửi cho AI Agent trong workspace của bạn:

```text
Bạn đang đóng vai trò Thành viên 3 — leehuy (Phân loại bằng Thống kê từ khóa — Keyword Statistics Classification) trong dự án Phân loại Spam Email bằng Jupyter Notebook (`.ipynb`).

BẮT BUỘC đọc kỹ `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` trước khi làm.

Database đầu vào & Thư viện hàm lõi Trưởng nhóm đã viết sẵn:
- `data/train.csv` (350 email), `data/validation.csv` (75 email), `data/test.csv` (75 email), gồm 7 cột `email_id,subject,body,clean_text,stat_text,label,label_num`.
- CHỈ học bảng trọng số từ `data/train.csv`, tuyệt đối KHÔNG dùng `validation.csv` hay `test.csv` khi đếm từ.
- BẮT BUỘC import và gọi hàm đã có sẵn từ `src/` (thêm `sys.path.insert(0, str(Path("..").resolve()))` ở cell đầu notebook):
  `from src.preprocessing import load_emails_from_csv`
  `from src.statistics import train_statistics, save_statistics, load_statistics, score_statistics, get_top_keywords_by_class`
  Tuyệt đối KHÔNG tự viết lại công thức tính trọng số khác quy ước chung và KHÔNG sửa các file trong `src/`.

Yêu cầu bắt buộc:
1. Chỉ tạo/sửa các file thuộc quyền sở hữu của Thành viên 3:
   - `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
   - `data/processed/keyword_stats.json`
   - `outputs/stat_val_scores.csv`, `outputs/stat_test_scores.csv`
   - `outputs/figures/stat_*.png`
   - `docs/statistics_method.md`
2. Xây dựng notebook `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb` rõ ràng bằng tiếng Việt (Markdown + Code):
   - Đọc `data/train.csv`, dùng cột `stat_text`, đếm document frequency ở cấp độ email (`set(tokens)`), lọc `df_spam + df_ham >= 3`, tính `P_s = (df_s+1)/(N_s+2)`, `P_h = (df_h+1)/(N_h+2)`, `W = clip(ln(P_s/P_h), -2.0, +2.0)`.
   - Lưu `data/processed/keyword_stats.json` (UTF-8, indent=2, sort_keys=True) với các key `version, min_df, n_spam, n_ham, vocab_size, weights, df_spam, df_ham`.
   - Vẽ biểu đồ Top 15 từ khóa Spam (W > 0) và Top 15 từ khóa Ham (W < 0) lưu ra `outputs/figures/stat_top_keywords.png`.
   - Viết hàm `score_statistics(stat_tokens, model, top_k=5)`: lấy tập từ duy nhất trong `model['weights']`, sắp xếp theo `(-abs(w), token)`, chọn tối đa 5 từ, tính `S_stat = round((2/5) * sum(w), 4)`.
   - Thêm cell `assert` kiểm chứng: ví dụ tính tay `1.84`, từ chưa thấy trọng số 0 (T05), tie-break ổn định (T11).
   - Chấm điểm trên `data/validation.csv` và `data/test.csv`, vẽ phân bố `stat_score` trên validation (`outputs/figures/stat_score_distribution.png`), xuất `outputs/stat_val_scores.csv` và `outputs/stat_test_scores.csv` đúng 5 cột `email_id,label,label_num,stat_score,top_keywords`.
3. Thực thi toàn bộ notebook không lỗi và tóm tắt công thức + kết quả vào `docs/statistics_method.md`.
```
