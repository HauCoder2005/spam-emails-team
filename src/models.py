"""Shared data models and exception hierarchy for Email Spam Filter.

Do NOT modify this file on feature branches without approval from the project lead.
All modules must adhere to the contract defined in `docs/QUY_UOC_CHUNG_VA_PHAN_CONG.md`.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional

LabelType = Literal["spam", "ham"]
ModeType = Literal["rule_only", "statistics_only", "combined"]


class SpamFilterError(Exception):
    """Lỗi gốc của hệ thống Email Spam Filter."""


class DataLoadError(SpamFilterError):
    """Lỗi đọc file TXT/CSV hoặc sai định dạng dữ liệu."""


class ConfigError(SpamFilterError):
    """Lỗi cấu hình JSON (rules.json, settings.json)."""


class ModelNotReadyError(SpamFilterError):
    """Chưa có file thống kê keyword_stats.json hoặc model không hợp lệ."""


@dataclass(frozen=True)
class Email:
    email_id: str
    subject: str
    body: str
    label: Optional[LabelType] = None
    source_group: Optional[str] = None


@dataclass(frozen=True)
class RuleMatch:
    rule_id: str
    pattern: str
    weight: float
    description: str = ""


@dataclass(frozen=True)
class KeywordEvidence:
    token: str
    weight: float


@dataclass(frozen=True)
class ClassificationResult:
    email_id: str
    prediction: LabelType
    mode: ModeType
    rule_score: float
    stat_score: float
    total_score: float
    threshold: float
    matched_rules: list[RuleMatch] = field(default_factory=list)
    top_keywords: list[KeywordEvidence] = field(default_factory=list)
