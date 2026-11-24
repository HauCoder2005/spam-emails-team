# Giao nhiệm vụ 04 — Phí Đặng Nguyên Huy... (Đánh giá, So sánh & Phân tích lỗi — `.ipynb`)

- **Phụ trách:** **Phí Đặng Nguyên Huy...** (Thành viên 4)
- **Nhánh Git BẮT BUỘC:** `nguyenhuy/evaluation-qa` *(chỉ code & push lên đúng nhánh này, KHÔNG push thẳng lên `main`)*
- **File Notebook chính:** `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`
- **Tài liệu bắt buộc đọc trước:** `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- **File bạn sở hữu (chỉ tạo/sửa các file này):**
  - `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`
  - `outputs/evaluation_report.json`
  - `outputs/figures/eval_*.png`
  - `docs/test_report.md`

---

## 1. Hướng dẫn kéo code mới từ `main`, tạo nhánh & khởi tạo môi trường (Chạy trước khi code)

```bash
# 1. Nếu bạn ĐÃ clone repo trước đó: kéo code & task mới nhất từ main về
git checkout main
git pull origin main

# 2. Tạo và chuyển sang đúng nhánh mang tên bạn (nếu đã tạo trước đó thì chạy: git checkout nguyenhuy/evaluation-qa)
git checkout -b nguyenhuy/evaluation-qa

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

- **Các tập dữ liệu chuẩn:** `data/train.csv` (350), `data/validation.csv` (75), `data/test.csv` (75).
- **Bảng dự đoán tổng hợp 3 chế độ trên tập Test (do Trưởng nhóm xuất ở Notebook 05):**
  - `outputs/hybrid_test_predictions.csv` gồm các cột:
    `email_id,label,label_num,rule_score,stat_score,combined_score,pred_rule,pred_stat,pred_combined,matched_rules,top_keywords`
- *(Trong lúc chờ Trưởng nhóm xuất `outputs/hybrid_test_predictions.csv`, bạn vẫn viết và test sẵn toàn bộ hàm metric, vẽ heatmap và test chia cho 0 bằng dữ liệu giả lập ngay trong Notebook.)*

---

## 3. Cấu trúc chi tiết từng phần trong `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`

1. **Kiểm tra chống rò rỉ dữ liệu (Data Leakage Audit — T13):**
   - Đọc `data/train.csv`, `data/validation.csv`, `data/test.csv`, kiểm tra giao nhau theo `clean_text` giữa 3 cặp tập `(train, val)`, `(train, test)`, `(val, test)` → xác nhận `0` bản ghi trùng.
2. **Xây dựng bộ hàm tính Metric chuẩn (Spam = lớp dương `1`):**
   - Tính `TP, TN, FP, FN`, `Accuracy`, `Precision`, `Recall`, `F1-score`, `FPR`.
   - **Xử lý an toàn chia cho 0 (T12):** Không để lỗi `ZeroDivisionError`; nếu mẫu số = 0 thì trả `0.0` kèm thông báo cảnh báo trong `warnings`.
   - Thêm cell `assert` kiểm chứng công thức tính tay (`TP=32, TN=34, FP=3, FN=6` → Acc 88.0%, Prec 91.4%, Rec 84.2%, F1 87.7%, FPR 8.1%) và test chia cho 0.
3. **So sánh 3 chế độ + Baseline trên cùng tập `data/test.csv` (T15):**
   - Đọc `outputs/hybrid_test_predictions.csv`.
   - Tính kết quả cho **4 mô hình**:
     1. **Majority Baseline** (luôn đoán lớp phổ biến nhất trên `train.csv`)
     2. **Rule-only** (`pred_rule`)
     3. **Statistics-only** (`pred_stat`)
     4. **Combined / Hybrid** (`pred_combined`)
   - In bảng DataFrame so sánh tổng hợp (Accuracy, Precision, Recall, F1, FPR, TP/TN/FP/FN).
4. **Trực quan hóa kết quả (lưu ảnh làm báo cáo/slide):**
   - Vẽ **3 Confusion Matrix Heatmap** đặt cạnh nhau cho `Rule-only`, `Statistics-only`, `Combined` → lưu `outputs/figures/eval_confusion_matrices.png`.
   - Vẽ **biểu đồ cột nhóm so sánh Accuracy / Precision / Recall / F1** giữa 4 mô hình → lưu `outputs/figures/eval_mode_comparison.png`.
5. **Phân tích lỗi (Error Analysis — điểm cộng rất lớn khi bảo vệ!):**
   - Lọc ra các email bị mô hình `Combined` đoán sai:
     - **False Positive (Ham nhưng bị đoán là Spam):** hiển thị `subject`, `rule_score`, `stat_score`, `matched_rules`, `top_keywords` và viết nhận xét vì sao bị nhầm.
     - **False Negative (Spam nhưng bị lọt thành Ham):** hiển thị tương tự và giải thích nguyên nhân (ví dụ spam ít từ khóa quen thuộc, hoặc điểm âm từ Ham kéo xuống).
6. **Xuất báo cáo tổng hợp:**
   - Lưu `outputs/evaluation_report.json` (UTF-8, đầy đủ số liệu thật của 4 mô hình + xác nhận không leakage).
   - Điền bảng số liệu thật và nhận xét vào `docs/test_report.md` (nhấn mạnh mục tiêu Accuracy ≥ 80% là mốc tham khảo, báo cáo trung thực số liệu thực nghiệm).

---

## 4. Hướng dẫn tạo file, code hàm & lệnh chạy / push Git

### A. Tạo file & khung code chuẩn trong `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`
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

   from src.preprocessing import load_emails_from_csv
   from src.evaluation import (
       evaluate, evaluate_majority_baseline, check_data_leakage, export_evaluation_json
   )
   ```
2. **Các hàm phụ trợ cần viết trong Notebook:**
   - `run_leakage_audit()` → gọi `load_emails_from_csv` cho `train/validation/test.csv` và gọi `check_data_leakage(...)` từ `src.evaluation`, `assert not report["has_leakage"]`.
   - `build_comparison_table(pred_df, train_labels)` → gọi `evaluate_majority_baseline` và `evaluate` cho 3 cột `pred_rule`, `pred_stat`, `pred_combined`, trả về DataFrame so sánh 4 mô hình.
   - `plot_confusion_matrices(metrics_by_mode, out_path)` → vẽ 3 Confusion Matrix Heatmap đặt cạnh nhau, lưu `outputs/figures/eval_confusion_matrices.png`.
   - `plot_metric_comparison(comp_df, out_path)` → vẽ biểu đồ cột nhóm so sánh Accuracy/Precision/Recall/F1, lưu `outputs/figures/eval_mode_comparison.png`.
   - `analyze_errors(pred_df, test_df)` → lọc False Positive (`label=='ham'` & `pred_combined=='spam'`) và False Negative (`label=='spam'` & `pred_combined=='ham'`) để phân tích nguyên nhân.

### B. Lệnh chạy kiểm thử & Bộ lệnh Git Push chuẩn (Copy chạy trực tiếp)

**1. Chạy kiểm tra trước khi push:**
```bash
jupyter notebook notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb
python scripts/setup_data.py --verify
python -m unittest discover -s tests -v
```

**2. Tạo nhánh & chuyển sang nhánh `nguyenhuy/evaluation-qa` rồi push lần đầu (copy chạy từng dòng):**
```bash
# Bước 1: Tạo nhánh mới và chuyển sang luôn (nếu đã tạo trước đó rồi thì chạy: git checkout nguyenhuy/evaluation-qa)
git checkout -b nguyenhuy/evaluation-qa

# Bước 2: Chắc chắn đang ở đúng nhánh của bạn (phải in ra: nguyenhuy/evaluation-qa)
git branch --show-current

# Bước 3: Xem danh sách file thay đổi (chỉ được có file của bạn)
git status

# Bước 4: Add ĐÚNG file của bạn
git add notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb outputs/evaluation_report.json outputs/figures/eval_*.png docs/test_report.md

# Bước 5: Commit đúng tiền tố feat(nguyenhuy):
git commit -m "feat(nguyenhuy): danh gia 3 che do, ve confusion matrix va error analysis"

# Bước 6: Push lên đúng nhánh của bạn
git push -u origin nguyenhuy/evaluation-qa
```

**3. Các lần sửa tiếp theo (push bổ sung):**
```bash
git add notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb outputs/evaluation_report.json outputs/figures/eval_*.png docs/test_report.md
git commit -m "fix(nguyenhuy): cap nhat bao cao danh gia va phan tich loi"
git push
```

**4. Khi Trưởng nhóm đã xuất `outputs/hybrid_test_predictions.csv` lên `main`, kéo về rồi chạy lại Notebook 04:**
```bash
git fetch origin
git merge origin/main
# Chạy lại Restart & Run All trong Notebook 04 rồi push lại
git add notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb outputs/evaluation_report.json outputs/figures/eval_*.png docs/test_report.md
git commit -m "docs(nguyenhuy): cap nhat so lieu danh gia chinh thuc tu hybrid test"
git push
```

> **CẤM:** Tuyệt đối KHÔNG chạy `git push origin main` và KHÔNG sửa file của thành viên khác.

---

## 5. Prompt chuẩn để giao cho AI Agent

Copy nguyên văn gửi cho AI Agent trong workspace của bạn:

```text
Bạn đang đóng vai trò Thành viên 4 — Phí Đặng Nguyên Huy... (Đánh giá, So sánh & Phân tích lỗi) trong dự án Phân loại Spam Email bằng Jupyter Notebook (`.ipynb`).

BẮT BUỘC đọc kỹ `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` trước khi làm. Chỉ làm việc trên nhánh `nguyenhuy/evaluation-qa`.

Database đầu vào & Thư viện hàm lõi Trưởng nhóm đã viết sẵn:
- `data/train.csv`, `data/validation.csv`, `data/test.csv`.
- Bảng dự đoán 3 chế độ trên test: `outputs/hybrid_test_predictions.csv` (nếu file chưa có khi chạy độc lập thì tạo dữ liệu mẫu giả lập để test hàm, đồng thời ghi chú rõ khi có file thật chỉ cần chạy lại Run All).
- BẮT BUỘC import và gọi hàm đã có sẵn từ `src/` (thêm `sys.path.insert(0, str(Path("..").resolve()))` ở cell đầu notebook):
  `from src.preprocessing import load_emails_from_csv`
  `from src.evaluation import evaluate, evaluate_majority_baseline, check_data_leakage, export_evaluation_json`
  Tuyệt đối KHÔNG tự viết lại hàm `evaluate` khác quy ước chung và KHÔNG sửa các file trong `src/`.

Yêu cầu bắt buộc:
1. Chỉ tạo/sửa các file thuộc quyền sở hữu của Thành viên 4:
   - `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`
   - `outputs/evaluation_report.json`
   - `outputs/figures/eval_*.png`
   - `docs/test_report.md`
2. Xây dựng notebook `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb` rõ ràng bằng tiếng Việt (Markdown + Code):
   - Cell kiểm tra data leakage giữa `train.csv`, `validation.csv`, `test.csv` theo `clean_text` (T13).
   - Hàm `evaluate(y_true, y_pred)` quy ước `'spam'` là lớp dương, xử lý an toàn mọi phép chia cho 0 với `warnings` tiếng Việt (T12), kèm cell `assert` test ví dụ tính tay (`TP=32, TN=34, FP=3, FN=6`) và test chia cho 0.
   - Đánh giá so sánh 4 mô hình trên cùng `test.csv`: Majority Baseline, Rule-only, Statistics-only, Combined (T15).
   - Vẽ & lưu 3 Confusion Matrix Heatmap cạnh nhau (`outputs/figures/eval_confusion_matrices.png`) và biểu đồ cột so sánh Accuracy/Precision/Recall/F1 (`outputs/figures/eval_mode_comparison.png`).
   - Phần Error Analysis: liệt kê các email False Positive và False Negative kèm `matched_rules`, `top_keywords` để giải thích vì sao đoán nhầm.
   - Lưu báo cáo JSON ra `outputs/evaluation_report.json` và viết báo cáo tóm tắt vào `docs/test_report.md` (tuyệt đối chỉ báo cáo số liệu thật, không bịa số).
3. Thực thi toàn bộ notebook đảm bảo chạy không lỗi.
```
