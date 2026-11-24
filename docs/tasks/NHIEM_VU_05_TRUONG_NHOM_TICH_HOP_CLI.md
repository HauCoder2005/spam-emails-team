# Giao nhiệm vụ 05 — Bạn (Trưởng nhóm: Tích hợp Hybrid, Tối ưu ngưỡng & Gán nhãn Demo — `.ipynb`)

- **Phụ trách:** **Bạn** (Trưởng nhóm đồ án / Thành viên 5)
- **Nhánh Git:** Quản lý `main` và làm tính năng trên `lead/hybrid-integration`
- **File Notebook chính:** `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb` và `notebooks/06_TONG_HOP_TOAN_BO_DU_AN.ipynb`
- **Tài liệu quy ước chung:** `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- **File bạn sở hữu:**
  - Bộ thư viện hàm lõi dùng chung cho cả 4 bạn gọi vào: `src/models.py`, `src/preprocessing.py`, `src/rules.py`, `src/statistics.py`, `src/evaluation.py`, `src/classifier.py`, `tests/test_core.py`
  - `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb`
  - `notebooks/06_TONG_HOP_TOAN_BO_DU_AN.ipynb` *(file gộp toàn bộ 5 phần lại thành 1 notebook tổng duy nhất để nộp & thuyết trình)*
  - `config/settings.json`
  - `outputs/hybrid_val_predictions.csv`, `outputs/hybrid_test_predictions.csv`
  - `outputs/labeled_new_emails.csv` (kết quả gán nhãn tự động cho email mới chưa có nhãn)
  - `requirements.txt`, `README.md`, `.gitignore`

---

## 1. Dataset Setup — Required Before Starting Tasks & Bản đồ 5 Notebook

Chạy lệnh sau để đảm bảo toàn bộ dữ liệu trên máy khớp 100% `data/manifest.json` trước khi tích hợp:

```bash
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/setup_data.py --verify
```

| Bước | Thành viên | Notebook | Đầu ra bàn giao |
|---|---|---|---|
| **1** | **Dương Hiển Thắng** | `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb` | `data/train.csv`, `data/validation.csv`, `data/test.csv`, `data/unlabeled_sample.csv` |
| **2** | **Nguyễn Kiệt** | `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb` | `config/rules.json`, `outputs/rule_val_scores.csv`, `outputs/rule_test_scores.csv` |
| **3** | **leehuy** | `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb` | `data/processed/keyword_stats.json`, `outputs/stat_val_scores.csv`, `outputs/stat_test_scores.csv` |
| **4** | **Bạn (Trưởng nhóm)** | `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb` | `config/settings.json`, `outputs/hybrid_test_predictions.csv`, `outputs/labeled_new_emails.csv` |
| **5** | **Phí Đặng Nguyên Huy...** | `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb` | `outputs/evaluation_report.json`, biểu đồ Confusion Matrix & Error Analysis |

---

## 2. Cấu trúc chi tiết từng phần trong `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb`

1. **Gộp điểm từ Nguyễn Kiệt & leehuy trên tập Validation (`data/validation.csv`):**
   - Đọc `outputs/rule_val_scores.csv` và `outputs/stat_val_scores.csv`, ghép theo `email_id`.
   - Tính `combined_score = rule_score + stat_score`.
2. **Tối ưu ngưỡng phân loại trên `validation.csv` (không đụng `test.csv`):**
   - Quét lưới ngưỡng ứng viên (ví dụ từ `-3.0` đến `+4.0`, bước `0.25`) cho từng chế độ (`rule_only`, `statistics_only`, `combined`).
   - Chọn ngưỡng tối ưu theo **F1-score** (vẽ biểu đồ F1/Accuracy theo ngưỡng lưu ra `outputs/figures/hybrid_threshold_tuning.png`).
   - Lưu 3 ngưỡng đã chốt (`T_rule`, `T_stat`, `T_combined`) vào `config/settings.json`.
3. **Áp ngưỡng cố định lên tập Test độc lập (`data/test.csv`):**
   - Ghép `outputs/rule_test_scores.csv` và `outputs/stat_test_scores.csv` theo `email_id`.
   - Tính `combined_score = rule_score + stat_score`.
   - Gán nhãn dự đoán cho cả 3 chế độ (`pred_rule`, `pred_stat`, `pred_combined`: `"spam"` nếu điểm ≥ ngưỡng tương ứng, ngược lại `"ham"`).
   - Xuất `outputs/hybrid_test_predictions.csv` đúng 11 cột chuẩn để **Phí Đặng Nguyên Huy...** chạy Notebook 04 đánh giá & vẽ Confusion Matrix.
4. **Demo Gán nhãn tự động cho email mới chưa có nhãn (`data/unlabeled_sample.csv`):**
   - Đọc `data/unlabeled_sample.csv` (30 email chưa nhãn) cùng `config/rules.json`, `data/processed/keyword_stats.json`, `config/settings.json`.
   - Chạy trọn pipeline chấm `rule_score`, `stat_score`, `combined_score`, tự động gán nhãn `predicted_label` (`spam`/`ham`) và `predicted_label_num` (`1`/`0`), kèm lý do (`matched_rules` + `top_keywords`).
   - Lưu ra `outputs/labeled_new_emails.csv` và in bảng mẫu 10 email đẹp mắt (lưu ý: **không in "% xác suất Spam"**).
5. **Cell Demo tương tác nhập thử email bất kỳ:**
   - Viết hàm `predict_single_email(subject, body, mode="combined")` để khi thuyết trình giảng viên đọc bất kỳ 1 email nào, bạn gõ vào cell và chạy ra ngay nhãn `spam`/`ham` + giải thích từng quy tắc & từ khóa khớp!

---

## 3. Quy trình gộp code 4 thành viên về `main` (Ràng buộc theo tên nhánh từng người)

1. Bạn đẩy sẵn `main` (đã có `src/*`, `scripts/setup_data.py`, `data/manifest.json`, `AGENTS.md`, `requirements.txt`, `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`, `docs/tasks/NHIEM_VU_0x...`).
2. Gửi mỗi bạn file `NHIEM_VU_0x` tương ứng; cả 4 bạn `git pull origin main`, tạo **đúng nhánh mang tên mình** và chạy `python scripts/setup_data.py`.
3. **Thứ tự Merge về `main`:**
   ```bash
   git checkout main

   # Đợt 1 — Dương Hiển Thắng
   git merge --no-ff origin/thang/eda-preprocessing

   # Đợt 2 — Nguyễn Kiệt & leehuy (có thể merge song song)
   git merge --no-ff origin/kiet/rule-classification
   git merge --no-ff origin/leehuy/statistics-classification

   # Đợt 3 — Chạy Notebook 05 của Trưởng nhóm trên nhánh lead/hybrid-integration rồi merge
   git merge --no-ff lead/hybrid-integration

   # Đợt 4 — Phí Đặng Nguyên Huy... (chạy Notebook 04 sau khi pull hybrid_test_predictions.csv)
   git merge --no-ff origin/nguyenhuy/evaluation-qa

   # Kiểm thử toàn bộ hệ thống trước khi đẩy main cuối cùng
   python scripts/setup_data.py --verify
   python -m unittest discover -s tests -v
   ```

---

## 4. Prompt chuẩn cho AI Agent (dùng cho chính bạn)

```text
Bạn đang đóng vai trò Trưởng nhóm (Thành viên 5 — Tích hợp Hybrid, Tối ưu ngưỡng & Gán nhãn Demo) trong dự án Phân loại Spam Email bằng Jupyter Notebook (`.ipynb`).

BẮT BUỘC đọc kỹ `AGENTS.md` và `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md` trước khi làm. Làm việc trên nhánh `lead/hybrid-integration`.

Dữ liệu đầu vào trong repo (sau khi đã merge nhánh của Thành viên 1, 2, 3):
- `data/validation.csv`, `data/test.csv`, `data/unlabeled_sample.csv`
- `config/rules.json`, `data/processed/keyword_stats.json`
- `outputs/rule_val_scores.csv`, `outputs/rule_test_scores.csv`
- `outputs/stat_val_scores.csv`, `outputs/stat_test_scores.csv`

Yêu cầu bắt buộc:
1. Chỉ tạo/sửa các file của Trưởng nhóm:
   - `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb`
   - `config/settings.json`
   - `outputs/hybrid_val_predictions.csv`, `outputs/hybrid_test_predictions.csv`, `outputs/labeled_new_emails.csv`
   - `outputs/figures/hybrid_threshold_tuning.png`
2. Xây dựng notebook `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb` rõ ràng bằng tiếng Việt (Markdown + Code):
   - Gộp điểm `rule_score` và `stat_score` trên `validation.csv`, tính `combined_score = rule_score + stat_score`.
   - Quét ngưỡng ứng viên trên `validation.csv` để tìm ngưỡng tối ưu theo F1-score cho cả 3 chế độ (`rule_only`, `statistics_only`, `combined`), vẽ biểu đồ `outputs/figures/hybrid_threshold_tuning.png` và lưu 3 ngưỡng đã chốt vào `config/settings.json`.
   - Áp 3 ngưỡng cố định lên tập `test.csv`, xuất `outputs/hybrid_test_predictions.csv` đúng 11 cột `email_id,label,label_num,rule_score,stat_score,combined_score,pred_rule,pred_stat,pred_combined,matched_rules,top_keywords`.
   - Đọc `data/unlabeled_sample.csv`, chạy pipeline gán nhãn tự động (`predicted_label`, `predicted_label_num`) kèm giải thích quy tắc khớp và top-5 từ khóa (KHÔNG in "% xác suất"), lưu ra `outputs/labeled_new_emails.csv`.
   - Cung cấp hàm `predict_single_email(subject, body, mode="combined")` ở cuối notebook kèm 3 ví dụ chạy thử (1 Spam rõ, 1 Ham rõ, 1 email pha trộn cả tín hiệu Spam và Ham).
3. Thực thi toàn bộ notebook đảm bảo chạy mượt không lỗi.
```
