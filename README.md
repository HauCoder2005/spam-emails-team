# Email Spam Filter (EDA, Processing, Hybrid Rule-based & Keyword Statistics)

Hệ thống phân loại email tiếng Anh (`spam` / `ham`) chạy **Python 3.11+**, kết hợp **Jupyter Notebook (`.ipynb`)** cho từng thành viên và bộ thư viện hàm lõi dùng chung trong `src/`.

---

## Dataset Setup — Required Before Starting Tasks

> **Quan trọng:** Các file CSV dữ liệu dung lượng lớn **không được commit trực tiếp lên GitHub** (đã loại trừ trong `.gitignore`). Sau khi clone repository, mỗi thành viên **bắt buộc** chạy lệnh dưới đây để tự động tải dataset từ Kaggle (`venky73/spam-mails-dataset`, phiên bản cố định v1) và tái tạo đầy đủ dữ liệu chuẩn giống nhau 100%:

```bash
git clone <repository-url>
cd <project-directory>

pip install -r requirements.txt

python scripts/setup_data.py
```

### Các lệnh quản lý dữ liệu khác

```bash
# Kiểm tra toàn bộ raw & processed dataset hiện có (không tải lại)
python scripts/setup_data.py --verify

# Chỉ tải và xác thực raw dataset vào data/raw/spam_ham_dataset.csv
python scripts/setup_data.py --download-only

# Chủ động tải lại từ Kaggle và tái tạo toàn bộ file CSV đã xử lý
python scripts/setup_data.py --force
```

Sau khi chạy `python scripts/setup_data.py` thành công, bạn sẽ có sẵn:
- `data/raw/spam_ham_dataset.csv` (5.171 email gốc, SHA-256 khớp `data/manifest.json`)
- `data/processed/spam_ham_dataset.csv` (bản sao đã xác thực)
- `data/train.csv` (350 email: 175 `spam` / 175 `ham`)
- `data/validation.csv` (75 email: 38 `spam` / 37 `ham`)
- `data/test.csv` (75 email: 37 `spam` / 38 `ham`)
- `data/unlabeled_sample.csv` (30 email chưa nhãn dùng cho demo gán nhãn)

---

## Cấu trúc thư mục

```text
Spam_Email/
├── config/
│   ├── rules.json                      # Bộ quy tắc lọc từ khóa Spam/Ham
│   └── settings.json                   # Ngưỡng phân loại cho 3 chế độ
├── data/
│   ├── manifest.json                   # Metadata, version Kaggle, SHA-256 & cấu hình chia tập
│   ├── raw/                            # Chứa spam_ham_dataset.csv sau khi chạy setup_data.py (ignored)
│   ├── processed/                      # Chứa spam_ham_dataset.csv & keyword_stats.json (ignored)
│   ├── train.csv / validation.csv / test.csv / unlabeled_sample.csv (sinh tự động, ignored)
├── docs/
│   ├── QUY_UOC_CHUNG_VA_PHAN_CONG.md   # Quy ước chung & bản đồ dữ liệu cho 5 thành viên
│   └── tasks/                          # Giao nhiệm vụ & prompt chuẩn cho từng thành viên
├── notebooks/                          # Jupyter Notebooks (.ipynb) của 5 thành viên
├── outputs/                            # Kết quả chấm điểm CSV, evaluation_report.json & figures/
├── scripts/
│   └── setup_data.py                   # Script tự động tải, kiểm tra & khởi tạo dataset
├── src/
│   ├── models.py                       # Dataclass & Exception dùng chung
│   ├── preprocessing.py                # Chuẩn hóa & tách token dùng chung
│   ├── rules.py                        # Rule Engine dùng chung
│   ├── statistics.py                   # Statistics Engine dùng chung
│   ├── evaluation.py                   # Metrics & kiểm tra data leakage
│   └── classifier.py                   # Hybrid Classifier (3 chế độ)
├── tests/                              # Unit tests (test_core.py, test_setup_data.py)
├── requirements.txt
└── README.md
```

## Kiểm thử hệ thống

```bash
python -m unittest discover -s tests -v
```

## Tài liệu nội bộ cho nhóm

- Quy ước code chung & phân công: `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`
- Giao nhiệm vụ & prompt cho từng thành viên: `docs/tasks/`
