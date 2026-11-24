# Rule-based Classification Specification

## 1. Phạm vi
Phân loại email Spam/Ham bằng quy tắc từ khóa và cụm từ liền kề.

## 2. Dữ liệu
- Train: 350 email; chỉ dùng để khảo sát và xây dựng quy tắc.
- Validation: 75 email; dùng chọn ngưỡng.
- Test: 75 email; chỉ dùng đánh giá cuối.

## 3. Quy tắc
- Tổng số quy tắc: 28.
- Spam có trọng số dương; Ham có trọng số âm.
- Mỗi quy tắc chỉ được tính tối đa một lần trên mỗi email.
- Điểm cuối được giới hạn trong [-5.0, +5.0].

## 4. Ngưỡng
- T_rule được chọn trên Validation: **-1.75**.
- Dự đoán Spam nếu rule_score >= T_rule; ngược lại dự đoán Ham.

## 5. Kết quả Validation
- Accuracy: 0.8533
- Precision: 0.7755
- Recall: 1.0000
- F1-score: 0.8736
- FPR: 0.2973

## 6. Kết quả Test
- Accuracy: 0.9333
- Precision: 0.8810
- Recall: 1.0000
- F1-score: 0.9367
- FPR: 0.1316

## 7. Hạn chế
- Bộ luật phụ thuộc vào từ khóa/cụm từ đã xuất hiện trong Train.
- Email diễn đạt mới hoặc dùng từ đồng nghĩa có thể không khớp quy tắc.
- Rule score là điểm phân loại, không phải xác suất Spam.

## 8. Danh sách quy tắc

| ID | Pattern | Weight | Description |
|---|---|---:|---|
| R001 | `microsoft` | +4 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=13, Ham DF=0). |
| R002 | `2004` | +4 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=12, Ham DF=0). |
| R003 | `paliourg` | +4 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=12, Ham DF=0). |
| R004 | `product` | +4 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=12, Ham DF=0). |
| R005 | `your browser` | +4 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=12, Ham DF=0). |
| R006 | `biz` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=11, Ham DF=0). |
| R007 | `offers` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=11, Ham DF=0). |
| R008 | `pills` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=11, Ham DF=0). |
| R009 | `and paste` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=10, Ham DF=0). |
| R010 | `copy and` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=10, Ham DF=0). |
| R011 | `copy and paste` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=10, Ham DF=0). |
| R012 | `health` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=10, Ham DF=0). |
| R013 | `hello` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=10, Ham DF=0). |
| R014 | `into your browser` | +3 | Tín hiệu nghiêng về SPAM theo document frequency trên tập Train (Spam DF=10, Ham DF=0). |
| R015 | `enron` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=65). |
| R016 | `hpl` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=54). |
| R017 | `daren` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=51). |
| R018 | `ect` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=45). |
| R019 | `meter` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=45). |
| R020 | `hou` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=43). |
| R021 | `hou ect` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=43). |
| R022 | `pm to` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=40). |
| R023 | `ect ect` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=39). |
| R024 | `hou ect ect` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=39). |
| R025 | `am to` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=36). |
| R026 | `ect cc` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=35). |
| R027 | `ect ect cc` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=35). |
| R028 | `forwarded` | -3 | Tín hiệu nghiêng về HAM theo document frequency trên tập Train (Spam DF=0, Ham DF=35). |
