"""Shared text preprocessing and dataset loading utilities for Email Spam Filter."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from src.models import DataLoadError, Email

STOPWORDS: frozenset[str] = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "can", "could", "did", "do", "does", "for", "from", "had", "has", "have",
    "he", "her", "here", "hers", "him", "his", "how", "i", "if", "in", "into",
    "is", "it", "its", "just", "me", "more", "my", "no", "not", "of", "on",
    "or", "our", "out", "she", "should", "so", "some", "than", "that", "the",
    "their", "them", "then", "there", "these", "they", "this", "to", "too",
    "up", "us", "very", "was", "we", "were", "what", "when", "where", "which",
    "who", "why", "will", "with", "would", "you", "your", "yours",
})

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def split_subject_body(raw_text: str) -> tuple[str, str]:
    """Tách dòng đầu 'Subject: ...' thành (subject, body)."""
    if not raw_text:
        return "", ""
    lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    first_line = lines[0].strip()
    if first_line.lower().startswith("subject:"):
        subject = first_line[len("subject:"):].strip()
        body = "\n".join(lines[1:]).strip()
        return subject, body
    return "", raw_text.strip()


def normalize_text(text: str) -> str:
    """Chuẩn hóa chữ thường, giữ token [a-z0-9]+ ngăn cách bởi 1 khoảng trắng."""
    if not text:
        return ""
    return " ".join(_TOKEN_RE.findall(text.lower()))


def tokenize(text: str) -> list[str]:
    """Tách văn bản thành list token chữ thường theo ranh giới từ (GIỮ stopwords)."""
    if not text:
        return []
    return _TOKEN_RE.findall(text.lower())


def filter_stat_tokens(tokens: list[str]) -> list[str]:
    """Loại bỏ STOPWORDS và token ngắn hơn 2 ký tự (dùng cho Statistics Engine)."""
    return [tok for tok in tokens if len(tok) >= 2 and tok not in STOPWORDS]


def prepare_email_tokens(email: Email) -> tuple[list[str], list[str]]:
    """Ghép subject + body và trả về (rule_tokens, stat_tokens)."""
    combined = f"{email.subject} {email.body}".strip()
    rule_tokens = tokenize(combined)
    stat_tokens = filter_stat_tokens(rule_tokens)
    return rule_tokens, stat_tokens


def load_email_from_txt(file_path: str, email_id: str = "TXT_001") -> Email:
    """Đọc 1 email từ file .txt; raise DataLoadError nếu lỗi hoặc rỗng."""
    path = Path(file_path)
    if not path.is_file():
        raise DataLoadError(f"Không tìm thấy tệp TXT: {file_path}")
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DataLoadError(f"Không thể đọc tệp TXT '{file_path}': {exc}") from exc

    subject, body = split_subject_body(raw_text)
    if not subject and not body:
        raise DataLoadError(f"Tệp TXT '{file_path}' không có nội dung email.")
    return Email(email_id=email_id, subject=subject, body=body)


def load_emails_from_csv(
    file_path: str,
    require_label: bool = False,
) -> tuple[list[Email], list[dict]]:
    """Đọc danh sách Email từ CSV chuẩn; ghi nhận lỗi từng dòng mà không làm mất dòng hợp lệ."""
    path = Path(file_path)
    if not path.is_file():
        raise DataLoadError(f"Không tìm thấy tệp CSV: {file_path}")

    required_cols = {"email_id", "subject", "body"}
    if require_label:
        required_cols.add("label")

    valid_emails: list[Email] = []
    row_errors: list[dict] = []

    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise DataLoadError(f"Tệp CSV '{file_path}' bị rỗng hoặc thiếu dòng tiêu đề.")
            missing = required_cols - set(reader.fieldnames)
            if missing:
                raise DataLoadError(
                    f"Tệp CSV '{file_path}' thiếu cột bắt buộc: {', '.join(sorted(missing))}"
                )

            for idx, row in enumerate(reader, start=2):
                email_id = (row.get("email_id") or "").strip() or f"ROW_{idx}"
                subject = (row.get("subject") or "").strip()
                body = (row.get("body") or "").strip()
                raw_label = (row.get("label") or "").strip().lower()
                source_group = (row.get("source_group") or "").strip() or None

                if not subject and not body:
                    row_errors.append({
                        "row": idx,
                        "email_id": email_id,
                        "reason": "Cả tiêu đề và nội dung đều rỗng.",
                    })
                    continue

                label = None
                if raw_label:
                    if raw_label not in ("spam", "ham"):
                        row_errors.append({
                            "row": idx,
                            "email_id": email_id,
                            "reason": f"Nhãn không hợp lệ: '{raw_label}' (chỉ nhận 'spam' hoặc 'ham').",
                        })
                        continue
                    label = raw_label
                elif require_label:
                    row_errors.append({
                        "row": idx,
                        "email_id": email_id,
                        "reason": "Thiếu nhãn phân loại bắt buộc.",
                    })
                    continue

                valid_emails.append(
                    Email(
                        email_id=email_id,
                        subject=subject,
                        body=body,
                        label=label,
                        source_group=source_group,
                    )
                )
    except OSError as exc:
        raise DataLoadError(f"Lỗi đọc tệp CSV '{file_path}': {exc}") from exc

    return valid_emails, row_errors
