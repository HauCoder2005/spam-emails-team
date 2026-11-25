# B?o c?o ??nh gi?, So s?nh M? h?nh & Ki?m th? Ch?t l??ng (Evaluation & QA)

- **Ng??i th?c hi?n:** Ph? ??ng Nguy?n Huynh (Th?nh vi?n 4 ? `nguyenhuy/evaluation-qa`)
- **Notebook th?c nghi?m:** `notebooks/04_DANH_GIA_SO_SANH_VA_PHAN_TICH_LOI.ipynb`
- **T?p k?t qu? JSON:** `outputs/evaluation_report.json`

---

## 1. Thi?t l?p th?c nghi?m & Ki?m tra ch?ng Data Leakage

- **Ngu?n d? li?u:** T?p d? li?u Kaggle `venky73/spam-mails-dataset` (v1), chu?n h?a b?ng `scripts/setup_data.py` v?i `random_seed = 42`.
- **Ph?n chia t?p d? li?u (kh? tr?ng l?p tr??c khi chia):**
  - `data/train.csv`: **350 email** ? ch? d?ng ?? thi?t k? quy t?c v? hu?n luy?n tr?ng s? t? kh?a.
  - `data/validation.csv`: **75 email** ? ch? d?ng ?? t?i ?u ng??ng ph?n lo?i.
  - `data/test.csv`: **75 email** (`37 spam` / `38 ham`) ? gi? ??c l?p ho?n to?n cho b??c ??nh gi? cu?i c?ng.
- **Ki?m tra Data Leakage (Test T13):** H?m `check_data_leakage()` x?c nh?n **0 b?n ghi tr?ng l?p** sau chu?n h?a gi?a 3 c?p t?p `(train, validation)`, `(train, test)` v? `(validation, test)`.
- **Quy ??c l?p d??ng & Thang ?i?m:** L?p **`spam` (`1`)** l? l?p d??ng (Positive) trong m?i c?ng th?c metric. C?c ?i?m s? `S_rule ? [-5, +5]`, `S_stat ? [-4, +4]` v? `S_total = S_rule + S_stat` l? ?i?m ph?n lo?i so v?i ng??ng c? ??nh t? Validation (`T_rule = 0.00`, `T_stat = -0.75`, `T_combined = -0.75`), **kh?ng ph?i x?c su?t `% Spam`**.

---

## 2. K?t qu? so s?nh 4 m? h?nh tr?n t?p Test ??c l?p (`N = 75`)

| M? h?nh | Ng??ng | TP | TN | FP | FN | Accuracy | Precision | Recall | F1-score | FPR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Majority Baseline** *(lu?n ?o?n `ham`)* | ? | 0 | 38 | 0 | 37 | 50.67% | 0.00% | 0.00% | 0.00% | 0.00% |
| **Rule-only** | `0.00` | 37 | 30 | 8 | 0 | 89.33% | 82.22% | 100.00% | 90.24% | 21.05% |
| **Statistics-only** | `-0.75` | 30 | 38 | 0 | 7 | 90.67% | 100.00% | 81.08% | 89.55% | 0.00% |
| **Combined (Hybrid)** | `-0.75` | 33 | 37 | 1 | 4 | 93.33% | 97.06% | 89.19% | 92.96% | 2.63% |

### Nh?n x?t th?c nghi?m
1. **??t m?c ti?u ch?t l??ng:** C? 3 ph??ng ph?p ??u v??t xa m?c tham kh?o `Accuracy >= 80%` v? b? xa `Majority Baseline` (`50.67%`).
2. **S? b? tr? c?a m? h?nh lai (Combined):**
   - `Rule-only` ??t Recall `100.00%` (`FN = 0`) nh?ng nh?y c?m v?i t? ??n l? n?n ph?t sinh `FP = 8` (`FPR = 21.05%`).
   - `Statistics-only` ??t Precision `100.00%` (`FP = 0`) nh?ng b? s?t `FN = 7` th? r?c.
   - Khi k?t h?p (`Combined`), ?i?m th?ng k? v? ?i?m lu?t b? tr? cho nhau, ??a **Accuracy l?n 93.33%** v? **F1-score l?n 92.96%** (`FP = 1`, `FN = 4`).

---

## 3. Ph?n t?ch l?i (Error Analysis ? Ch? ?? Combined)

### False Positives (Ham b? ?o?n nh?m th?nh Spam ? `1` ca)
- **`E0464`** (*fw : candle lighting*): `S_rule = +2.00`, `S_stat = -0.80`, `S_total = +1.20` | Lu?t kh?p: `R012:guaranteed(+2.0)` | T? kh?a n?i b?t: `2001(-2.00); guaranteed(+2.00); pm(-2.00); smith(-2.00); stop(+2.00)`.

### False Negatives (Spam b? b? s?t th?nh Ham ? `4` ca)
- **`E0433`** (*never see a doctor again to get the medocations you want vo 4*): `S_rule = +0.00`, `S_stat = -2.20`, `S_total = -2.20` | Lu?t kh?p: `Kh?ng c?` | T? kh?a n?i b?t: `03(-2.00); doctor(+2.00); pm(-2.00); tell(-1.79); 26(-1.70)`.
- **`E0447`** (*coca cola , mbna america , nascar partner with otcbb : imts*): `S_rule = +1.50`, `S_stat = -4.00`, `S_total = -2.50` | Lu?t kh?p: `R016:investment(+1.5)` | T? kh?a n?i b?t: `02(-2.00); 03(-2.00); 04(-2.00); 08(-2.00); agreement(-2.00)`.
- **`E0461`** (*quality rx meds supplier goode*): `S_rule = +0.00`, `S_stat = -2.40`, `S_total = -2.40` | Lu?t kh?p: `Kh?ng c?` | T? kh?a n?i b?t: `cc(-2.00); ic(-2.00); ls(-2.00); meds(+2.00); pg(-2.00)`.
- **`E0492`** (*today ' s daily sales for angelo only*): `S_rule = +0.00`, `S_stat = -3.54`, `S_total = -3.54` | Lu?t kh?p: `Kh?ng c?` | T? kh?a n?i b?t: `daily(-2.00); contract(-1.83); mary(-1.79); agree(-1.61); chad(-1.61)`.

---

## 4. K?t qu? ki?m th? ch?c n?ng & t?nh hu?ng bi?n (QA Checklist)

- **Unit & Integration Test Suite (`python -m unittest discover -s tests -v`):** To?n b? 13 b?i ki?m th? l?i (`test_core.py` v? `test_setup_data.py`) ??u **PASS**.
- **T12 (Chia cho 0 trong Evaluation):** Khi t?t c? d? ?o?n l? `ham` (`TP = FP = 0`), h?m `evaluate()` tr? v? `0.0` cho `Precision` v? `F1`, ??ng th?i ghi nh?n th?ng b?o ti?ng Vi?t trong tr??ng `warnings` m? kh?ng ph?t sinh ngo?i l? `ZeroDivisionError`.
- **T13 (Ki?m tra tr?ng l?p xuy?n t?p):** ?? x?c nh?n `0` b?n ghi tr?ng `clean_text` gi?a `train`, `validation`, `test`.
- **T14 & T15 (T?nh t?i l?p & So s?nh ??ng nh?t):** Ch?y l?i notebook cho ra k?t qu? kh?p 100% khi d?ng c?ng d? li?u v? c?u h?nh; c? 3 ch? ?? v? `Majority Baseline` ???c ?o tr?n c?ng t?p `data/test.csv`.
