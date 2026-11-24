"""Hybrid Rule-based + Keyword Statistics classifier for Email Spam Filter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.models import (
    ClassificationResult,
    ConfigError,
    DataLoadError,
    Email,
    KeywordEvidence,
    ModeType,
    ModelNotReadyError,
)
from src.preprocessing import prepare_email_tokens
from src.rules import score_rules
from src.statistics import score_statistics


def load_settings(settings_path: str = "config/settings.json") -> dict:
    """Đọc và kiểm tra tệp cấu hình ngưỡng config/settings.json."""
    path = Path(settings_path)
    if not path.is_file():
        raise ConfigError(f"Không tìm thấy tệp cấu hình: {settings_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ConfigError(f"Tệp cấu hình '{settings_path}' bị lỗi JSON: {exc}") from exc

    thresholds = data.get("thresholds")
    if not isinstance(thresholds, dict):
        raise ConfigError(f"Tệp '{settings_path}' thiếu mục 'thresholds'.")
    for mode in ("rule_only", "statistics_only", "combined"):
        val = thresholds.get(mode)
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise ConfigError(f"Ngưỡng cho chế độ '{mode}' không hợp lệ trong '{settings_path}'.")
    return data


def save_settings(settings: dict, settings_path: str = "config/settings.json") -> str:
    """Lưu cấu hình ngưỡng sau khi tối ưu trên Validation."""
    path = Path(settings_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


def classify_email(
    email: Email,
    mode: ModeType,
    rules: list[dict],
    stats_model: Optional[dict],
    settings: dict,
) -> ClassificationResult:
    """Phân loại 1 email theo 1 trong 3 chế độ: rule_only, statistics_only, combined."""
    if not email.subject.strip() and not email.body.strip():
        raise DataLoadError("Email rỗng (không có tiêu đề và nội dung), không thể phân loại.")

    rule_tokens, stat_tokens = prepare_email_tokens(email)
    rule_score, matched_rules = score_rules(rule_tokens, rules)

    stat_score = 0.0
    top_keywords: list[KeywordEvidence] = []
    if mode in ("statistics_only", "combined"):
        if stats_model is None:
            raise ModelNotReadyError(
                "Chưa tải bảng thống kê từ khóa (keyword_stats.json) để chạy chế độ thống kê/kết hợp."
            )
        stat_score, top_keywords = score_statistics(stat_tokens, stats_model)
    elif stats_model is not None:
        stat_score, top_keywords = score_statistics(stat_tokens, stats_model)

    if mode == "rule_only":
        total_score = rule_score
    elif mode == "statistics_only":
        total_score = stat_score
    elif mode == "combined":
        total_score = round(rule_score + stat_score, 4)
    else:
        raise ConfigError(f"Chế độ phân loại không hợp lệ: '{mode}'.")

    threshold = float(settings["thresholds"][mode])
    prediction = "spam" if total_score >= threshold else "ham"

    return ClassificationResult(
        email_id=email.email_id,
        prediction=prediction,
        mode=mode,
        rule_score=rule_score,
        stat_score=stat_score,
        total_score=total_score,
        threshold=threshold,
        matched_rules=matched_rules,
        top_keywords=top_keywords,
    )
