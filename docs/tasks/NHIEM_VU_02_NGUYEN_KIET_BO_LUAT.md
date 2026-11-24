# Giao nhiệm vụ 02 — Nguyễn Kiệt (Phân loại theo Quy tắc từ khóa — `.ipynb`)

- **Phụ trách:** **Nguyễn Kiệt** (Thành viên 2)
- **Nhánh Git BẮT BUỘC:** `kiet/rule-classification` *(chỉ code & push lên đúng nhánh này, KHÔNG push thẳng lên `main`)*
- **File Notebook chính:** `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb`
- **Tài liệu bắt buộc đọc trước:** `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- **File bạn sở hữu (chỉ tạo/sửa các file này):**
  - `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb`
  - `config/rules.json`
  - `outputs/rule_val_scores.csv`, `outputs/rule_test_scores.csv`
  - `outputs/figures/rule_*.png`
  - `docs/rule_specification.md`

---

## 1. Hướng dẫn tạo nhánh Git & Khởi tạo môi trường (Chạy trước khi code)

```bash
git clone <repository-url>
cd <project-directory>
git checkout main
git pull origin main

# Tạo và chuyển sang đúng nhánh mang tên bạn (BẮT BUỘC)
git checkout -b kiet/rule-classification

# Cài thư viện và tải + kiểm tra toàn bộ dữ liệu tự động
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

- **Tập Train (để khảo sát từ khóa & thiết kế quy tắc):** `data/train.csv` (350 email, 7 cột chuẩn).
- **Tập Validation (để chấm điểm & tìm ngưỡng `T_rule` sơ bộ):** `data/validation.csv` (75 email).
- **Tập Test (chỉ chạy chấm điểm cuối cùng, KHÔNG mở ra xem nội dung để sửa luật):** `data/test.csv` (75 email).
- **Cột văn bản bạn sử dụng:** cột **`clean_text`** (đã chuẩn hóa chữ thường và **GIỮ stopwords** để khớp cụm nhiều từ như `claim your prize`).

---

## 3. Cấu trúc chi tiết từng phần trong `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb`

1. **Khảo sát cụm từ đặc trưng trên `data/train.csv`:**
   - Đọc `data/train.csv`, thống kê các từ đơn và cụm 2–3 từ (n-grams) xuất hiện nổi bật ở `spam` vs `ham` trên tập train để làm cơ sở khoa học thiết kế bộ quy tắc.
2. **Xây dựng & lưu bộ quy tắc `config/rules.json`:**
   - Tạo khoảng **25–30 quy tắc** tiếng Anh sát với dữ liệu email Enron-Spam (gồm cả điểm dương `+1` đến `+4` cho dấu hiệu Spam và điểm âm `-1` đến `-3` cho dấu hiệu Ham công việc).
   - Viết hàm validate JSON: báo lỗi rõ ràng nếu thiếu trường `id`, `pattern`, `weight`, `description` hoặc `weight == 0`.
3. **Cài đặt thuật toán chấm điểm Rule-based (`score_rules`):**
   - Khớp theo **ranh giới chuỗi token liền kề** (tách `clean_text.split()` và `pattern` thành list token):
     - Không phân biệt hoa thường (`WINNER` = `winner`).
     - Không khớp nhầm từ con (`free` không khớp trong `freedom`, `win` không khớp trong `winner`).
   - Mỗi quy tắc chỉ tính **tối đa 1 lần / email** dù từ lặp lại nhiều lần (`free free free` chỉ tính 1 lần).
   - Cộng tổng điểm dương/âm rồi **chặn trong khoảng `[-5.0, +5.0]`**, đồng thời giữ nguyên danh sách các quy tắc khớp để giải thích.
4. **Chạy test kiểm chứng các tình huống biên ngay trong Notebook:**
   - Viết cell `assert` kiểm tra T01 (hoa/thường), T02 (từ con), T03 (từ lặp), T04 (vừa Spam vừa Ham), chặn biên ±5, và khớp cụm có stopwords (`claim your prize`).
5. **Chấm điểm trên `validation.csv` và `test.csv`, trực quan hóa & xuất file:**
   - Vẽ biểu đồ phân bố điểm `rule_score` giữa `spam` và `ham` trên tập `validation` (`outputs/figures/rule_score_distribution.png`).
   - Thử các ngưỡng ứng viên trên `validation.csv` để đề xuất ngưỡng `T_rule` ban đầu.
   - Xuất đúng 2 file CSV chuẩn 5 cột `email_id,label,label_num,rule_score,matched_rules`:
     - `outputs/rule_val_scores.csv`
     - `outputs/rule_test_scores.csv`

---

## 4. Hướng dẫn tạo file, code hàm & lệnh chạy / push Git

### A. Tạo file & khung code chuẩn
1. **File `config/rules.json`:** Tạo 25–30 quy tắc theo đúng schema JSON (`version`, `min_score: -5.0`, `max_score: 5.0`, `rules: [{id, pattern, weight, description}]`).
2. **Cell 1 trong `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb` (Import hàm lõi — BẮT BUỘC):**
   ```python
   import sys
   from pathlib import Path
   import pandas as pd
   import matplotlib.pyplot as plt

   PROJECT_ROOT = Path("..").resolve()
   if str(PROJECT_ROOT) not in sys.path:
       sys.path.insert(0, str(PROJECT_ROOT))

   from src.preprocessing import tokenize
   from src.rules import load_rules, score_rules
   ```
3. **Các hàm phụ trợ cần viết trong Notebook:**
   - `extract_top_ngrams(train_df, label, n=2, top_k=20)` → tìm cụm 1–2 từ nổi bật trên `data/train.csv` để chọn từ khóa đưa vào `config/rules.json`.
   - `score_dataframe(df, rules)` → lặp từng dòng cột `clean_text`, gọi `score_rules(str(text).split(), rules)` từ `src.rules`, trả về DataFrame 5 cột `email_id,label,label_num,rule_score,matched_rules`.
   - `plot_rule_score_distribution(val_scored_df, out_path)` → vẽ histogram phân bố `rule_score` giữa `spam` và `ham`, lưu `outputs/figures/rule_score_distribution.png`.

### B. Lệnh chạy kiểm thử & Push code lên đúng nhánh của bạn
```bash
# Mở Jupyter Notebook và chạy Restart & Run All
jupyter notebook notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb

# Kiểm tra unit test lõi của dự án vẫn PASS
python -m unittest discover -s tests -v

# Kiểm tra đúng nhánh và đúng file trước khi push
git branch --show-current
git status

# Commit và push LÊN ĐÚNG NHÁNH kiet/rule-classification
git add notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb config/rules.json outputs/rule_val_scores.csv outputs/rule_test_scores.csv outputs/figures/rule_*.png docs/rule_specification.md
git commit -m "feat(kiet): xay dung bo quy tac rules.json va cham diem rule-based"
git push -u origin kiet/rule-classification
```

---

## 5. Prompt chuẩn để giao cho AI Agent

Copy nguyên văn gửi cho AI Agent trong workspace của bạn:

```text
Bạn đang đóng vai trò Thành viên 2 — Nguyễn Kiệt (Phân loại theo Quy tắc từ khóa — Rule-based Classification) trong dự án Phân loại Spam Email bằng Jupyter Notebook (`.ipynb`).

BẮT BUỘC đọc kỹ `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` trước khi làm. Chỉ làm việc trên nhánh `kiet/rule-classification`.

Database đầu vào & Thư viện hàm lõi Trưởng nhóm đã viết sẵn:
- `data/train.csv` (350 email), `data/validation.csv` (75 email), `data/test.csv` (75 email), gồm 7 cột `email_id,subject,body,clean_text,stat_text,label,label_num`.
- CHỈ phân tích trên `data/train.csv` để chọn từ/cụm từ đưa vào quy tắc; tuyệt đối KHÔNG mở xem nội dung `data/test.csv` để chỉnh luật (tránh data leakage).
- BẮT BUỘC import và gọi hàm đã có sẵn từ `src/` (thêm `sys.path.insert(0, str(Path("..").resolve()))` ở cell đầu notebook):
  `from src.preprocessing import tokenize`
  `from src.rules import load_rules, score_rules`
  Tuyệt đối KHÔNG tự viết lại `score_rules` khác công thức và KHÔNG sửa các file trong `src/`.

Yêu cầu bắt buộc:
1. Chỉ tạo/sửa các file thuộc quyền sở hữu của Thành viên 2:
   - `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb`
   - `config/rules.json`
   - `outputs/rule_val_scores.csv`, `outputs/rule_test_scores.csv`
   - `outputs/figures/rule_*.png`
   - `docs/rule_specification.md`
2. Xây dựng notebook `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb` trình bày rõ ràng bằng tiếng Việt (Markdown + Code):
   - Khảo sát top từ/cụm từ Spam vs Ham trên `data/train.csv`.
   - Tạo và lưu `config/rules.json` gồm 25–30 quy tắc tiếng Anh sát dữ liệu Enron-Spam (có điểm dương Spam +1..+4 và điểm âm Ham -1..-3), đúng schema JSON (`version`, `min_score: -5.0`, `max_score: 5.0`, `rules: [{id, pattern, weight, description}]`), kèm hàm kiểm tra lỗi JSON.
   - Viết hàm `score_rules(tokens, rules)` khớp theo chuỗi token liền kề (không khớp từ con như `free` trong `freedom`), mỗi quy tắc tính tối đa 1 lần/email, chặn tổng điểm trong `[-5.0, +5.0]`, trả về `(rule_score, matched_rules)`.
   - Thêm cell `assert` kiểm chứng đầy đủ T01 (hoa/thường), T02 (từ con), T03 (từ lặp), T04 (điểm dương+âm), chặn biên ±5.
   - Chấm điểm `clean_text` trên `data/validation.csv` và `data/test.csv`, vẽ biểu đồ phân bố `rule_score` trên validation lưu ra `outputs/figures/rule_score_distribution.png`.
   - Xuất `outputs/rule_val_scores.csv` và `outputs/rule_test_scores.csv` đúng 5 cột `email_id,label,label_num,rule_score,matched_rules`.
3. Thực thi toàn bộ notebook đảm bảo chạy không lỗi, lưu đầy đủ file đầu ra và viết tóm tắt vào `docs/rule_specification.md`.
```
