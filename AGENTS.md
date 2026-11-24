# AGENTS.md — Quy tắc bắt buộc cho AI Agent khi hỗ trợ thành viên dự án

> Mọi AI coding agent (Antigravity, Cursor, GitHub Copilot, Claude Code, Codex, ChatGPT...) khi làm việc trong repository **Email Spam Filter** này **BẮT BUỘC** phải đọc và tuân thủ tuyệt đối toàn bộ các quy tắc dưới đây.

---

## 1. Quy tắc Git & Ràng buộc nhánh theo từng thành viên

Mỗi thành viên **CHỈ ĐƯỢC** làm việc và push code trên đúng nhánh mang tên của mình. **TUYỆT ĐỐI KHÔNG** commit hoặc push trực tiếp lên nhánh `main`.

| Thành viên | Nhánh Git bắt buộc | File được phép tạo / chỉnh sửa |
|---|---|---|
| **Dương Hiển Thắng** | `thang/eda-preprocessing` | `notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb`, `outputs/figures/eda_*.png`, `docs/data_description.md` |
| **Nguyễn Kiệt** | `kiet/rule-classification` | `notebooks/02_PHAN_LOAI_THEO_QUY_TAC_RULE.ipynb`, `config/rules.json`, `outputs/rule_val_scores.csv`, `outputs/rule_test_scores.csv`, `outputs/figures/rule_*.png`, `docs/rule_specification.md` |
| **leehuy** | `leehuy/statistics-classification` | `notebooks/03_PHAN_LOAI_THONG_KE_TU_KHOA.ipynb`, `data/processed/keyword_stats.json`, `outputs/stat_val_scores.csv`, `outputs/stat_test_scores.csv`, `outputs/figures/stat_*.png`, `docs/statistics_method.md` |
| **Phí Đặng Nguyên Huy...** | `nguyenhuy/evaluation-qa` | `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`, `outputs/evaluation_report.json`, `outputs/figures/eval_*.png`, `docs/test_report.md` |
| **Trưởng nhóm** | `main` / `lead/hybrid-integration` | `src/*`, `scripts/*`, `tests/*`, `config/settings.json`, `data/manifest.json`, `notebooks/05_TICH_HOP_HYBRID_GAN_NHAN_DEMO.ipynb`, `notebooks/06_TONG_HOP_TOAN_BO_DU_AN.ipynb`, `outputs/hybrid_*.csv`, `outputs/labeled_new_emails.csv`, `AGENTS.md`, `README.md`, `requirements.txt`, `.gitignore` |

### Lệnh kiểm tra nhánh trước khi sửa code
Trước khi chỉnh sửa bất kỳ file nào, Agent/thành viên phải kiểm tra đang ở đúng nhánh:
```bash
git branch --show-current
```
Nếu chưa đúng nhánh của thành viên, chuyển ngay bằng:
```bash
git checkout -b <ten-nhanh-cua-ban>
```

---

## 2. Danh sách file CẤM SỬA đối với 4 thành viên

Trừ Trưởng nhóm, **KHÔNG AI** (kể cả AI Agent) được phép sửa hoặc xóa các file nền sau:
- `src/models.py`, `src/preprocessing.py`, `src/rules.py`, `src/statistics.py`, `src/evaluation.py`, `src/classifier.py`
- `scripts/setup_data.py`
- `data/manifest.json`
- `tests/test_core.py`, `tests/test_setup_data.py`
- `.gitignore`, `requirements.txt`, `AGENTS.md`, `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- File notebook/output thuộc quyền sở hữu của thành viên khác.

---

## 3. Quy tắc dùng lại hàm lõi trong `src/` (BẮT BUỘC)

Mọi notebook `.ipynb` phải thêm đoạn sau ở **Cell đầu tiên** rồi import trực tiếp hàm chuẩn từ `src/`:

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path("..").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

- **KHÔNG** tự viết lại hàm `tokenize`, `filter_stat_tokens`, `score_rules`, `train_statistics`, `score_statistics`, `evaluate`, `classify_email` với công thức khác `src/`.
- **KHÔNG** cài thêm thư viện ML/DL ngoài `requirements.txt` (không dùng `scikit-learn`, `torch`, `transformers`, `nltk` cho bài phân loại này).

---

## 4. Quy tắc dữ liệu, bảo mật & chống Data Leakage

1. **Khởi tạo dữ liệu bằng lệnh chuẩn (không tải CSV thủ công):**
   ```bash
   python scripts/setup_data.py
   python scripts/setup_data.py --verify
   ```
2. **Không commit file CSV dữ liệu lớn hoặc secrets:** Tuyệt đối không chạy `git add -f` cho `data/raw/*`, `data/processed/*.csv`, `data/train.csv`, `data/validation.csv`, `data/test.csv`, `data/unlabeled_sample.csv`, `kaggle.json`, `.env`.
3. **Chống Data Leakage tuyệt đối:**
   - Chỉ khảo sát từ khóa & huấn luyện bảng thống kê trên `data/train.csv`.
   - Chỉ tối ưu ngưỡng phân loại trên `data/validation.csv`.
   - Tuyệt đối không mở `data/test.csv` để chọn từ khóa đưa vào `rules.json` hay tinh chỉnh ngưỡng.
4. **Chuẩn học thuật:**
   - `spam` (`1`) là lớp dương (Positive) trong mọi công thức metric.
   - Không bao giờ in hoặc gọi điểm số `S_rule`, `S_stat`, `S_total` là **"xác suất % Spam"**.
   - Không bịa số liệu trong báo cáo; chỉ ghi số liệu thực nghiệm thật sau khi chạy code.

---

## 5. Quy tắc kiểm chứng trước khi hoàn thành & Push

Trước khi báo xong hoặc `git push`, AI Agent và thành viên phải kiểm tra:
1. `python scripts/setup_data.py --verify` trả về exit code `0`.
2. Notebook `.ipynb` của thành viên chạy sạch từ đầu tới cuối (**Restart & Run All**) không có lỗi.
3. Chạy `git status` để chắc chắn **chỉ có đúng các file thuộc quyền sở hữu của mình** được thay đổi.
4. Push đúng lên nhánh của mình: `git push -u origin <ten-nhanh-cua-ban>`.
