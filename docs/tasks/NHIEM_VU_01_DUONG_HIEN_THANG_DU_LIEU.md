# Giao nhiệm vụ 01 — Dương Hiển Thắng (EDA, Tiền xử lý & Đánh nhãn dữ liệu — `.ipynb`)

- **Phụ trách:** **Dương Hiển Thắng** (Thành viên 1)
- **Nhánh Git BẮT BUỘC:** `thang/eda-preprocessing` *(chỉ code & push lên đúng nhánh này, KHÔNG push thẳng lên `main`)*
- **File Notebook chính:** `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb`
- **Tài liệu bắt buộc đọc trước:** `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- **File bạn sở hữu (chỉ tạo/sửa các file này):**
  - `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb`
  - `outputs/figures/eda_*.png` (các biểu đồ EDA lưu ra ảnh để làm slide/báo cáo)
  - `docs/data_description.md`
  - *(Các file CSV trong `data/` được sinh tự động bởi `python scripts/setup_data.py` và đã có trong `.gitignore`, KHÔNG commit lên Git.)*

---

## 1. Hướng dẫn tạo nhánh Git & Khởi tạo môi trường (Chạy trước khi code)

```bash
# 1. Clone repo (nếu chưa có) và đồng bộ nhánh main mới nhất
git clone <repository-url>
cd <project-directory>
git checkout main
git pull origin main

# 2. Tạo và chuyển sang đúng nhánh mang tên bạn (BẮT BUỘC)
git checkout -b thang/eda-preprocessing

# 3. Cài thư viện và tải + kiểm tra toàn bộ dữ liệu tự động
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/setup_data.py --verify
```

---

## 2. Dataset Setup — Required Before Starting Tasks

Trước khi mở Notebook, chạy lệnh sau tại thư mục gốc repo để tự động tải và khởi tạo toàn bộ dữ liệu (không cần tải CSV thủ công từ Kaggle):

```bash
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/setup_data.py --verify
```

Sau lệnh trên, repo của bạn đã có sẵn:
- **File dữ liệu gốc:** `data/raw/spam_ham_dataset.csv` và bản sao `data/processed/spam_ham_dataset.csv` (**5.171 email**, `ham`: **3.672**, `spam`: **1.499**, 4 cột gốc `['', 'label', 'text', 'label_num']`, SHA-256 khớp `data/manifest.json`).
- **Các tập chuẩn đã chia sẵn (seed = 42, 0 data leakage):** `data/train.csv` (350), `data/validation.csv` (75), `data/test.csv` (75), `data/unlabeled_sample.csv` (30). Trong Notebook 01 bạn vẫn thực hiện đầy đủ EDA, minh họa lại bước tiền xử lý/kiểm chứng dữ liệu bằng `src/preprocessing.py` và lưu biểu đồ EDA vào `outputs/figures/`.

---

## 3. Cấu trúc chi tiết từng phần trong `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb`

### Phần 1 — Khám phá dữ liệu (EDA)
1. **Tổng quan bảng dữ liệu:** Đọc `data/processed/spam_ham_dataset.csv` bằng `pandas`, in `.shape`, `.info()`, `.head(5)`, kiểm tra giá trị thiếu (`isnull().sum()`), kiểm tra số bản ghi trùng lặp và kiểm tra độ khớp giữa cột `label` và `label_num`.
2. **Phân bố nhãn (Label Distribution):** Thống kê số lượng & tỷ lệ % `spam` vs `ham`, vẽ biểu đồ cột + tròn lưu vào `outputs/figures/eda_label_distribution.png`.
3. **Phân tích độ dài văn bản:** Tách sơ bộ `subject` và `body`, tính số ký tự và số từ của từng email; so sánh trung bình/trung vị độ dài giữa `spam` và `ham`, vẽ histogram/boxplot lưu vào `outputs/figures/eda_length_distribution.png`.
4. **Top 20 từ khóa phổ biến nhất ở Spam vs Ham:** Sau khi loại stopwords, thống kê top 20 từ xuất hiện nhiều nhất ở mỗi lớp và vẽ biểu đồ cột ngang song song lưu vào `outputs/figures/eda_top_words.png`.
5. **Cell Markdown nhận xét EDA:** Viết 4–5 gạch đầu dòng rút ra từ biểu đồ (ví dụ: dữ liệu gốc mất cân bằng 71% ham / 29% spam nên cần lấy mẫu cân bằng 250/250; các từ đặc trưng của Spam và Ham khác biệt rõ rệt).

### Phần 2 — Tiền xử lý & Chuẩn hóa nhãn (Processing & Labeling)
1. **Tách `subject` và `body`:** Từ cột `text`, tách dòng đầu bắt đầu bằng `Subject:` thành `subject` (bỏ tiền tố `Subject:`), phần còn lại thành `body`.
2. **Làm sạch & Chuẩn hóa nhãn:**
   - Loại bỏ dòng rỗng (cả `subject` và `body` đều rỗng) và dòng sai nhãn.
   - Đảm bảo chuẩn hóa nhất quán: `label` ∈ `{"spam", "ham"}` và `label_num` ∈ `{1, 0}` (`spam = 1`, `ham = 0`).
3. **Tạo 2 cột văn bản chuẩn hóa:**
   - `clean_text`: ghép `subject + " " + body`, chuyển chữ thường, tách token bằng regex `[a-z0-9]+` rồi nối bằng dấu cách (**GIỮ stopwords** để Nguyễn Kiệt khớp cụm từ).
   - `stat_text`: từ `clean_text`, lọc bỏ `STOPWORDS` cố định (trong `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`) và bỏ token dài `< 2` (cho leehuy tính thống kê).
4. **Khử trùng lặp TRƯỚC khi chia tập:** Loại các email trùng `clean_text`, in rõ số lượng bị loại.
5. **Chia tập cân bằng (`seed = 42`) & Xuất CSV đúng 7 cột (`email_id,subject,body,clean_text,stat_text,label,label_num`):**
   - Lấy đúng **250 Spam + 250 Ham = 500 email**, gán `email_id` từ `E0001` → `E0500`:
     - `data/train.csv`: **350 email** (175 `spam` / 175 `ham`)
     - `data/validation.csv`: **75 email** (38 `spam` / 37 `ham`)
     - `data/test.csv`: **75 email** (37 `spam` / 38 `ham`)
   - **Kiểm tra chống rò rỉ dữ liệu:** Khẳng định bằng `assert` rằng giao của tập `clean_text` giữa `train`, `validation`, `test` đều bằng `0`.
6. **Tạo tập chưa gán nhãn để demo đánh nhãn (`data/unlabeled_sample.csv`):**
   - Lấy **30 email khác** từ phần còn lại của `spam_ham_dataset.csv` (không trùng 500 email trên), giữ các cột `email_id` (`U001`..`U030`), `subject`, `body`, `clean_text`, `stat_text` (ẩn cột nhãn, lưu riêng nhãn thật vào `data/unlabeled_ground_truth.csv` hoặc chỉ giữ cho Trưởng nhóm kiểm chứng) để Trưởng nhóm chạy gán nhãn tự động.

---

## 4. Hướng dẫn tạo file, code hàm & lệnh chạy / push Git

### A. Tạo file & khung code chuẩn trong `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb`
1. **Cell 1 (Import hàm lõi của Trưởng nhóm — BẮT BUỘC):**
   ```python
   import sys
   from pathlib import Path
   import pandas as pd
   import matplotlib.pyplot as plt
   import seaborn as sns

   PROJECT_ROOT = Path("..").resolve()
   if str(PROJECT_ROOT) not in sys.path:
       sys.path.insert(0, str(PROJECT_ROOT))

   from src.preprocessing import (
       STOPWORDS, split_subject_body, normalize_text, tokenize, filter_stat_tokens
   )
   ```
2. **Các hàm phụ trợ cần viết gọn trong Notebook để gọi lại sạch sẽ:**
   - `plot_label_distribution(df, out_path)` → vẽ biểu đồ cột + tròn tỷ lệ `spam`/`ham`, lưu `outputs/figures/eda_label_distribution.png`.
   - `plot_length_distribution(df, out_path)` → vẽ histogram/boxplot độ dài từ theo lớp, lưu `outputs/figures/eda_length_distribution.png`.
   - `plot_top_words_by_class(df, top_n=20, out_path=...)` → gọi `tokenize()` + `filter_stat_tokens()` từ `src.preprocessing`, vẽ top 20 từ Spam vs Ham, lưu `outputs/figures/eda_top_words.png`.
   - `verify_split_integrity(train_df, val_df, test_df)` → `assert` kiểm tra đủ 7 cột, đủ số lượng `350/75/75` và **0 bản ghi trùng `clean_text`** giữa 3 tập.

### B. Lệnh chạy kiểm thử & Push code lên đúng nhánh của bạn
```bash
# Mở Jupyter Notebook và chọn Restart & Run All
jupyter notebook notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb

# Kiểm tra lại dữ liệu chuẩn
python scripts/setup_data.py --verify

# Kiểm tra đúng nhánh và đúng file của mình trước khi push
git branch --show-current
git status

# Commit và push LÊN ĐÚNG NHÁNH thang/eda-preprocessing
git add notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb outputs/figures/eda_*.png docs/data_description.md
git commit -m "feat(thang): hoan thanh EDA, tien xu ly va kiem chung du lieu"
git push -u origin thang/eda-preprocessing
```

---

## 5. Prompt chuẩn để giao cho AI Agent

Copy nguyên văn gửi cho AI Agent trong workspace của bạn:

```text
Bạn đang đóng vai trò Thành viên 1 — Dương Hiển Thắng (EDA, Tiền xử lý & Đánh nhãn dữ liệu) trong dự án Phân loại Spam Email bằng Jupyter Notebook (`.ipynb`).

BẮT BUỘC đọc kỹ `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` trước khi làm. Chỉ làm việc trên nhánh `thang/eda-preprocessing`.

Database hiện có & Thư viện hàm lõi Trưởng nhóm đã viết sẵn:
- File dữ liệu gốc: `data/processed/spam_ham_dataset.csv` (5.171 dòng, 4 cột `['', 'label', 'text', 'label_num']`, gồm 3.672 ham và 1.499 spam; cột `text` mở đầu bằng `Subject: ...`).
- BẮT BUỘC import và gọi lại các hàm đã có sẵn trong `src/preprocessing.py` (thêm `sys.path.insert(0, str(Path("..").resolve()))` ở cell đầu notebook):
  `from src.preprocessing import STOPWORDS, split_subject_body, normalize_text, tokenize, filter_stat_tokens`
  Tuyệt đối KHÔNG tự viết lại hàm tokenize khác quy ước chung và KHÔNG sửa các file trong `src/`.

Yêu cầu bắt buộc:
1. Chỉ tạo/sửa các file thuộc quyền sở hữu của Thành viên 1:
   - `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb`
   - `data/train.csv`, `data/validation.csv`, `data/test.csv`, `data/unlabeled_sample.csv`
   - `outputs/figures/eda_*.png`
   - `docs/data_description.md`
2. Xây dựng notebook `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb` trình bày sạch đẹp bằng tiếng Việt (có các cell Markdown giải thích rõ từng bước + cell Code):
   - Phần 1 (EDA): kiểm tra shape/missing/duplicate/khớp nhãn `label`–`label_num`; vẽ & lưu biểu đồ phân bố nhãn (`eda_label_distribution.png`), biểu đồ phân bố độ dài email theo lớp (`eda_length_distribution.png`), biểu đồ top 20 từ khóa phổ biến nhất của Spam vs Ham sau khi bỏ stopwords (`eda_top_words.png`); viết nhận xét EDA rõ ràng.
   - Phần 2 (Processing & Labeling): tách `subject`/`body` từ cột `text`, chuẩn hóa nhãn `label` (`spam`/`ham`) và `label_num` (`1`/`0`), tạo `clean_text` (regex `[a-z0-9]+`, giữ stopwords) và `stat_text` (bỏ đúng bộ `STOPWORDS` trong `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` và token dài < 2).
   - Khử trùng theo `clean_text` TRƯỚC khi chia; lấy 250 spam + 250 ham (`seed=42`), chia thành `data/train.csv` (175/175), `data/validation.csv` (38/37), `data/test.csv` (37/38) đúng 7 cột `email_id,subject,body,clean_text,stat_text,label,label_num`. Thêm cell `assert` kiểm tra 0 trùng lặp giữa 3 tập.
   - Lấy thêm 30 email không trùng với 500 email trên để xuất `data/unlabeled_sample.csv` (bỏ cột nhãn, `email_id` là `U001`..`U030`) phục vụ demo gán nhãn.
3. Chạy thực thi toàn bộ notebook (execute notebook) để kiểm tra không có lỗi, đảm bảo các file CSV và biểu đồ PNG được sinh ra đầy đủ, rồi tóm tắt số liệu thật vào `docs/data_description.md`.
```
