"""Keyword document-frequency statistics engine for Email Spam Filter."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from src.models import Email, KeywordEvidence, ModelNotReadyError
from src.preprocessing import prepare_email_tokens


def train_statistics(train_emails: list[Email], min_df: int = 3) -> dict:
    """Tính bảng trọng số log-ratio từ tập train (đếm theo cấp độ email, làm trơn Laplace)."""
    df_spam: Counter[str] = Counter()
    df_ham: Counter[str] = Counter()
    n_spam = 0
    n_ham = 0

    for email in train_emails:
        if email.label not in ("spam", "ham"):
            raise ValueError(
                f"Email '{email.email_id}' có nhãn không hợp lệ '{email.label}' khi huấn luyện thống kê."
            )
        _, stat_tokens = prepare_email_tokens(email)
        unique_tokens = set(stat_tokens)
        if email.label == "spam":
            n_spam += 1
            df_spam.update(unique_tokens)
        else:
            n_ham += 1
            df_ham.update(unique_tokens)

    if n_spam == 0 or n_ham == 0:
        raise ValueError("Tập train phải có ít nhất 1 email 'spam' và 1 email 'ham'.")

    vocab = sorted(set(df_spam.keys()) | set(df_ham.keys()))
    weights: dict[str, float] = {}
    kept_df_spam: dict[str, int] = {}
    kept_df_ham: dict[str, int] = {}

    for token in vocab:
        s_count = df_spam[token]
        h_count = df_ham[token]
        if s_count + h_count < min_df:
            continue
        p_spam = (s_count + 1) / (n_spam + 2)
        p_ham = (h_count + 1) / (n_ham + 2)
        w = max(-2.0, min(2.0, math.log(p_spam / p_ham)))
        weights[token] = round(w, 6)
        kept_df_spam[token] = s_count
        kept_df_ham[token] = h_count

    return {
        "version": "1.0",
        "min_df": min_df,
        "n_spam": n_spam,
        "n_ham": n_ham,
        "vocab_size": len(weights),
        "weights": weights,
        "df_spam": kept_df_spam,
        "df_ham": kept_df_ham,
    }


def save_statistics(
    model: dict,
    output_path: str = "data/processed/keyword_stats.json",
) -> str:
    """Lưu bảng trọng số thống kê ra tệp JSON (UTF-8)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(path)


def load_statistics(
    model_path: str = "data/processed/keyword_stats.json",
) -> dict:
    """Đọc bảng trọng số từ JSON; raise ModelNotReadyError nếu chưa tạo hoặc sai cấu trúc."""
    path = Path(model_path)
    if not path.is_file():
        raise ModelNotReadyError(
            f"Chưa tìm thấy bảng thống kê từ khóa tại '{model_path}'. "
            "Hãy chạy Notebook 03 hoặc chức năng tạo bảng thống kê từ tập train trước."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ModelNotReadyError(
            f"Tệp bảng thống kê '{model_path}' bị lỗi hoặc không đọc được: {exc}"
        ) from exc

    if not isinstance(data, dict) or not isinstance(data.get("weights"), dict):
        raise ModelNotReadyError(
            f"Tệp bảng thống kê '{model_path}' sai định dạng (thiếu khóa 'weights')."
        )
    return data


def score_statistics(
    stat_tokens: list[str],
    model: dict,
    top_k: int = 5,
) -> tuple[float, list[KeywordEvidence]]:
    """Chấm điểm thống kê từ tối đa top_k từ có |W| lớn nhất (tie-break theo alphabet)."""
    weights_map: dict[str, float] = model.get("weights", {})
    candidates: list[tuple[str, float]] = [
        (tok, float(weights_map[tok]))
        for tok in set(stat_tokens)
        if tok in weights_map
    ]
    candidates.sort(key=lambda item: (-abs(item[1]), item[0]))
    selected = candidates[:top_k]

    stat_score = (2.0 / top_k) * sum(w for _, w in selected)
    evidences = [KeywordEvidence(token=tok, weight=round(w, 4)) for tok, w in selected]
    return round(stat_score, 4), evidences


def get_top_keywords_by_class(
    model: dict,
    n: int = 15,
) -> tuple[list[KeywordEvidence], list[KeywordEvidence]]:
    """Trả về (top_spam_keywords, top_ham_keywords) để trực quan hóa hoặc hiển thị."""
    weights_map: dict[str, float] = model.get("weights", {})
    spam_items = sorted(
        ((tok, float(w)) for tok, w in weights_map.items() if w > 0),
        key=lambda item: (-item[1], item[0]),
    )[:n]
    ham_items = sorted(
        ((tok, float(w)) for tok, w in weights_map.items() if w < 0),
        key=lambda item: (item[1], item[0]),
    )[:n]

    top_spam = [KeywordEvidence(token=tok, weight=round(w, 4)) for tok, w in spam_items]
    top_ham = [KeywordEvidence(token=tok, weight=round(w, 4)) for tok, w in ham_items]
    return top_spam, top_ham
