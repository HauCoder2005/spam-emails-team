# Mô tả dữ liệu và tiền xử lý

## Nguồn và kiểm tra chất lượng

Dữ liệu đầu vào `data/processed/spam_ham_dataset.csv` có 5.171 email, bốn cột nguồn (`Unnamed: 0`, `label`, `text`, `label_num`). Trong đó có 3.672 email ham (71,01%) và 1.499 email spam (28,99%). Không có giá trị thiếu hay hàng trùng hoàn toàn. Cả 5.171 cặp `label`–`label_num` nhất quán (`ham = 0`, `spam = 1`).

Hàm dùng chung `split_subject_body` loại tiền tố `Subject:` và tách tiêu đề khỏi thân thư. Sau khi bỏ hàng có nhãn không hợp lệ/không khớp hoặc email rỗng (16 hàng), bỏ một hàng có văn bản chuẩn hóa rỗng và khử 267 bản ghi trùng theo `clean_text`, còn 4.887 email duy nhất đủ điều kiện lấy mẫu.

## Đặc trưng văn bản

- `subject`, `body`: tách bằng `src.preprocessing.split_subject_body`; khoảng trắng đầu/cuối và khoảng trắng lặp được chuẩn hóa.
- `clean_text`: kết hợp subject và body, chuẩn hóa chữ thường theo token `[a-z0-9]+`; giữ stopwords.
- `stat_text`: lấy từ token của `clean_text`, loại đúng 80 stopwords và token ngắn hơn 2 ký tự bằng các hàm `tokenize` và `filter_stat_tokens` trong `src/preprocessing.py`.

Độ dài dưới đây là số token trong toàn bộ nội dung email trước khi lấy mẫu:

| Nhãn | Số email | Trung bình số từ | Trung vị số từ |
|---|---:|---:|---:|
| Ham | 3.672 | 155,02 | 84 |
| Spam | 1.499 | 185,15 | 86 |

Email spam có trung bình dài hơn trong dữ liệu này, trong khi trung vị hai lớp gần nhau; phân phối có độ lệch phải và các email rất dài thể hiện thành ngoại lệ.

## Các tập dữ liệu được tạo

Từ dữ liệu đã khử trùng, lấy ngẫu nhiên 250 spam và 250 ham bằng seed 42. Sau đó chia theo lớp để đạt đúng kích thước quy ước. `email_id` duy nhất từ `E0001` đến `E0500`; các CSV có đúng bảy cột `email_id,subject,body,clean_text,stat_text,label,label_num`.

| Tập | Tổng | Spam | Ham |
|---|---:|---:|---:|
| `data/train.csv` | 350 | 175 | 175 |
| `data/validation.csv` | 75 | 38 | 37 |
| `data/test.csv` | 75 | 37 | 38 |

Ba tập có giao rỗng theo `clean_text`, được kiểm tra bằng các assertion trong notebook. Tập demo `data/unlabeled_sample.csv` gồm 30 email khác với 500 email đã chọn, ID `U001`–`U030`; chỉ có năm cột văn bản/ID, không xuất nhãn.

Các CSV được tạo tự động và bị `.gitignore` loại khỏi Git theo quy ước dự án. Có thể tái tạo bằng cách chạy toàn bộ notebook:
[notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb](../notebooks/01_EDA_VA_TIEN_XU_LY_DU_LIEU.ipynb).

## Biểu đồ EDA

- [Phân bố nhãn](../outputs/figures/eda_label_distribution.png): số lượng và tỷ lệ nhãn trong dữ liệu gốc.
- [Phân bố độ dài](../outputs/figures/eda_length_distribution.png): histogram và boxplot số token theo lớp.
- [Top từ khóa](../outputs/figures/eda_top_words.png): 20 token phổ biến nhất của mỗi lớp sau khi bỏ stopwords; chỉ được đếm từ tập train để tránh sử dụng validation/test cho khảo sát từ khóa.
