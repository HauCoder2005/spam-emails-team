# Giao nhiệm vụ 03 — leehuy (Phân loại bằng Thống kê từ khóa — `.ipynb`)

- **Phụ trách:** **leehuy** (Thành viên 3)
- **Nhánh Git BẮT BUỘC:** `leehuy/statistics-classification` *(chỉ code & push lên đúng nhánh này, KHÔNG push thẳng lên `main`)*
- **File Notebook chính:** `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
- **Tài liệu bắt buộc đọc trước:** `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- **File bạn sở hữu (chỉ tạo/sửa các file này):**
  - `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
  - `data/processed/keyword_stats.json`
  - `outputs/stat_val_scores.csv`, `outputs/stat_test_scores.csv`
  - `outputs/figures/stat_*.png`
  - `docs/statistics_method.md`

---

## 1. Hướng dẫn kéo code mới từ `main`, tạo nhánh & khởi tạo môi trường (Chạy trước khi code)

```bash
# 1. Nếu bạn ĐÃ clone repo trước đó: kéo code & task mới nhất từ main về
git checkout main
git pull origin main

# 2. Tạo và chuyển sang đúng nhánh mang tên bạn (nếu đã tạo trước đó thì chạy: git checkout leehuy/statistics-classification)
git checkout -b leehuy/statistics-classification

# 3. Cài thư viện và tải + kiểm tra toàn bộ dữ liệu tự động
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/setup_data.py --verify
```

---

## 2. Dataset Setup — Required Before Starting Tasks

Trước khi bắt đầu làm task, chạy lệnh sau để tự động khởi tạo hoặc xác thực đầy đủ bộ dữ liệu trên máy bạn:

```bash
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/setup_data.py --verify
```

> **Lệnh `python scripts/setup_data.py` tự động làm hết:** tải `spam_ham_dataset.csv` từ Kaggle về `data/raw/spam_ham_dataset.csv`, **tự sao chép vào `data/processed/spam_ham_dataset.csv`**, và sinh sẵn `data/train.csv`, `data/validation.csv`, `data/test.csv`, `data/unlabeled_sample.csv` (bạn KHÔNG cần tải tay).

- **Tập Train (DUY NHẤT dùng để tính trọng số từ khóa):** `data/train.csv` (350 email: 175 `spam` / 175 `ham`, 7 cột chuẩn).
- **Tập Validation & Test (chỉ dùng để chấm điểm `S_stat`):** `data/validation.csv` (75 email), `data/test.csv` (75 email).
- **Cột văn bản bạn sử dụng:** cột **`stat_text`** (đã chuẩn hóa chữ thường, loại `STOPWORDS` và token dài `< 2`).
- **QUY TẮC CHỐNG DATA LEAKAGE:** Tuyệt đối chỉ học bảng trọng số từ `data/train.csv`, không bao giờ tính `df` trên `validation.csv` hay `test.csv`.

---

## 3. Cấu trúc chi tiết & Code minh họa thuật toán trong `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`

### Bước 1 — Huấn luyện bảng trọng số từ khóa từ `data/train.csv`
- Đếm **document frequency** theo cấp độ **email** (dùng `set(stat_tokens)`, 1 từ xuất hiện 10 lần trong cùng 1 email vẫn chỉ tính là 1 email có từ đó): `df_spam[w]` và `df_ham[w]`.
- Lọc bỏ từ hiếm: chỉ giữ từ có `df_spam[w] + df_ham[w] >= 3`.
- Công thức làm trơn Laplace & trọng số log-ratio:
  - $P_s(w) = \frac{df_s(w) + 1}{N_s + 2}$, $\quad P_h(w) = \frac{df_h(w) + 1}{N_h + 2}$, $\quad W(w) = \text{clip}\left(\ln\frac{P_s(w)}{P_h(w)}, -2.0, +2.0\right)$

**Logic thuật toán cốt lõi (đã cài sẵn trong `src/statistics.py` để bạn hiểu rõ bản chất):**
```python
import math
from collections import Counter

# Với mỗi email trong train: dùng set(stat_tokens) để đếm theo cấp độ EMAIL
# df_spam[w] = số email spam chứa từ w ; df_ham[w] = số email ham chứa từ w
if s_count + h_count >= min_df:              # Lọc từ xuất hiện < 3 email
    p_spam = (s_count + 1) / (n_spam + 2)    # Làm trơn Laplace lớp Spam
    p_ham  = (h_count + 1) / (n_ham + 2)     # Làm trơn Laplace lớp Ham
    w = max(-2.0, min(2.0, math.log(p_spam / p_ham)))  # Chặn trong [-2, +2]
```

**Code gọi trực tiếp trong Cell Notebook của bạn:**
```python
train_emails, _ = load_emails_from_csv(str(PROJECT_ROOT / "data/train.csv"), require_label=True)
model = train_statistics(train_emails, min_df=3)
save_statistics(model, str(PROJECT_ROOT / "data/processed/keyword_stats.json"))
print(f"Đã huấn luyện: n_spam={model['n_spam']}, n_ham={model['n_ham']}, vocab_size={model['vocab_size']}")
```

---

### Bước 2 — Trực quan hóa Top 15 từ khóa Spam & Ham
Vẽ biểu đồ cột ngang **Top 15 từ khóa thiên về Spam (`W > 0`)** và **Top 15 từ khóa thiên về Ham (`W < 0`)**, lưu vào `outputs/figures/stat_top_keywords.png`:

```python
top_spam, top_ham = get_top_keywords_by_class(model, n=15)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
axes[0].barh([k.token for k in top_spam][::-1], [k.weight for k in top_spam][::-1], color="crimson")
axes[0].set_title("Top 15 từ khóa thiên về SPAM (W > 0)")
axes[0].set_xlabel("Trọng số W")

axes[1].barh([k.token for k in top_ham][::-1], [k.weight for k in top_ham][::-1], color="steelblue")
axes[1].set_title("Top 15 từ khóa thiên về HAM (W < 0)")
axes[1].set_xlabel("Trọng số W")

plt.tight_layout()
plt.savefig(PROJECT_ROOT / "outputs/figures/stat_top_keywords.png", dpi=150)
plt.show()
```

---

### Bước 3 — Thuật toán chấm điểm thống kê (`score_statistics`)
- Lấy tập từ duy nhất trong `stat_text`, bỏ qua từ chưa thấy trong bảng (trọng số `0`, không lỗi — T05).
- Chọn tối đa **top 5 từ có `|W|` lớn nhất**; nếu hòa điểm thì sắp xếp phụ theo thứ tự bảng chữ cái `key=lambda x: (-abs(x[1]), x[0])` để kết quả tái lập 100% (T11).
- Công thức: $S_{\text{stat}} = \frac{2}{5} \sum_{i} W_i \in [-4.0, +4.0]$.

**Logic thuật toán cốt lõi (đã cài sẵn trong `src/statistics.py`):**
```python
candidates = [(tok, model["weights"][tok]) for tok in set(stat_tokens) if tok in model["weights"]]
candidates.sort(key=lambda item: (-abs(item[1]), item[0]))  # Tie-break theo alphabet
selected = candidates[:5]                                   # Tối đa 5 từ có |W| lớn nhất
stat_score = round((2.0 / 5) * sum(w for _, w in selected), 4)
```

---

### Bước 4 — Kiểm chứng công thức bằng `assert` ngay trong Notebook
Chạy cell này để chứng minh công thức khớp 100% với ví dụ tính tay trong `02_GIAI_THICH_THUAT_TOAN.md`:

```python
# 1. Kiểm chứng ví dụ tính tay: (2/5) * (2.0 + 1.5 + 1.1) = 1.84 + từ lạ (T05)
mock_model = {"weights": {"a": 2.0, "b": 1.5, "c": 1.1}}
s, ev = score_statistics(["a", "b", "c", "unseen_word"], mock_model, top_k=5)
assert s == 1.84, f"Sai công thức: {s} != 1.84"

# 2. Kiểm chứng tie-break ổn định theo alphabet khi hòa |W| (T11)
tie_model = {"weights": {k: 1.0 for k in ["zeta", "alpha", "beta", "gamma", "delta", "epsilon"]}}
_, ev_tie = score_statistics(list(tie_model["weights"].keys()), tie_model, top_k=5)
assert [k.token for k in ev_tie] == ["alpha", "beta", "delta", "epsilon", "gamma"]
print("PASS toàn bộ kiểm chứng công thức (1.84, T05, T11)!")
```

---

### Bước 5 — Chấm điểm trên `validation.csv` & `test.csv`, vẽ biểu đồ & xuất 2 file CSV
```python
def score_stat_dataframe(df: pd.DataFrame, model: dict) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        tokens = str(row["stat_text"]).split() if pd.notna(row["stat_text"]) else []
        stat_score, top_kw = score_statistics(tokens, model, top_k=5)
        kw_str = "; ".join(f"{k.token}({k.weight:+.2f})" for k in top_kw)
        rows.append({
            "email_id": row["email_id"],
            "label": row["label"],
            "label_num": int(row["label_num"]),
            "stat_score": stat_score,
            "top_keywords": kw_str,
        })
    return pd.DataFrame(rows)

val_df = pd.read_csv(PROJECT_ROOT / "data/validation.csv")
test_df = pd.read_csv(PROJECT_ROOT / "data/test.csv")

stat_val = score_stat_dataframe(val_df, model)
stat_test = score_stat_dataframe(test_df, model)

stat_val.to_csv(PROJECT_ROOT / "outputs/stat_val_scores.csv", index=False)
stat_test.to_csv(PROJECT_ROOT / "outputs/stat_test_scores.csv", index=False)
```
Sau đó vẽ histogram phân bố `stat_score` giữa `spam` và `ham` trên `stat_val`, lưu ra `outputs/figures/stat_score_distribution.png`.

---

## 4. Hướng dẫn tạo file, code hàm & lệnh chạy / push Git

### A. Tạo file & khung code chuẩn trong `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`
1. **Cell 1 (Import hàm lõi của Trưởng nhóm — BẮT BUỘC):**
   ```python
   import sys
   from pathlib import Path
   import pandas as pd
   import matplotlib.pyplot as plt

   PROJECT_ROOT = Path("..").resolve()
   if str(PROJECT_ROOT) not in sys.path:
       sys.path.insert(0, str(PROJECT_ROOT))

   from src.preprocessing import load_emails_from_csv
   from src.statistics import (
       train_statistics, save_statistics, load_statistics,
       score_statistics, get_top_keywords_by_class
   )
   ```
2. **Các bước gọi hàm & hàm phụ trợ cần viết trong Notebook:**
   - Gọi `train_emails, _ = load_emails_from_csv(str(PROJECT_ROOT / "data/train.csv"), require_label=True)` → gọi `model = train_statistics(train_emails, min_df=3)` → gọi `save_statistics(model, str(PROJECT_ROOT / "data/processed/keyword_stats.json"))`.
   - `plot_top_keywords(model, n=15, out_path=...)` → gọi `get_top_keywords_by_class(model, n=15)` và vẽ 2 biểu đồ cột ngang Spam/Ham lưu `outputs/figures/stat_top_keywords.png`.
   - `score_stat_dataframe(df, model)` → duyệt từng dòng cột `stat_text`, gọi `score_statistics(str(text).split(), model, top_k=5)`, trả về DataFrame 5 cột `email_id,label,label_num,stat_score,top_keywords` rồi xuất `outputs/stat_val_scores.csv` và `outputs/stat_test_scores.csv`.
   - `plot_stat_score_distribution(val_scored_df, out_path)` → vẽ phân bố `stat_score` trên validation, lưu `outputs/figures/stat_score_distribution.png`.

### B. Lệnh chạy kiểm thử & Bộ lệnh Git Push chuẩn (Copy chạy trực tiếp)

**1. Chạy kiểm tra trước khi push:**
```bash
jupyter notebook notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb
python scripts/setup_data.py --verify
python -m unittest discover -s tests -v
```

**2. Tạo nhánh & chuyển sang nhánh `leehuy/statistics-classification` rồi push lần đầu (copy chạy từng dòng):**
```bash
# Bước 1: Tạo nhánh mới và chuyển sang luôn (nếu đã tạo trước đó rồi thì chạy: git checkout leehuy/statistics-classification)
git checkout -b leehuy/statistics-classification

# Bước 2: Chắc chắn đang ở đúng nhánh của bạn (phải in ra: leehuy/statistics-classification)
git branch --show-current

# Bước 3: Xem danh sách file thay đổi (chỉ được có file của bạn)
git status

# Bước 4: Add ĐÚNG file của bạn (file keyword_stats.json nằm trong data/processed/ nên đã được .gitignore bảo vệ khỏi đẩy nhầm CSV)
git add notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb outputs/stat_val_scores.csv outputs/stat_test_scores.csv outputs/figures/stat_*.png docs/statistics_method.md

# Bước 5: Commit đúng tiền tố feat(leehuy):
git commit -m "feat(leehuy): huan luyen thong ke tu khoa va cham diem S_stat"

# Bước 6: Push lên đúng nhánh của bạn
git push -u origin leehuy/statistics-classification
```

**3. Các lần sửa tiếp theo (push bổ sung):**
```bash
git add notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb outputs/stat_val_scores.csv outputs/stat_test_scores.csv outputs/figures/stat_*.png docs/statistics_method.md
git commit -m "fix(leehuy): cap nhat bieu do va ket qua thong ke tu khoa"
git push
```

**4. Nếu Trưởng nhóm báo cập nhật `main`, đồng bộ về nhánh của bạn:**
```bash
git fetch origin
git merge origin/main
git push
```

> **CẤM:** Tuyệt đối KHÔNG chạy `git push origin main` và KHÔNG dùng `git add -f data/...`.

---

## 5. Prompt chuẩn để giao cho AI Agent

Copy nguyên văn gửi cho AI Agent trong workspace của bạn:

```text
Bạn đang đóng vai trò Thành viên 3 — leehuy (Phân loại bằng Thống kê từ khóa — Keyword Statistics Classification) trong dự án Phân loại Spam Email bằng Jupyter Notebook (`.ipynb`).

BẮT BUỘC đọc kỹ `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` trước khi làm. Chỉ làm việc trên nhánh `leehuy/statistics-classification`.

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
