"""Rule-based keyword/phrase scoring engine for Email Spam Filter."""

from __future__ import annotations

import json
from pathlib import Path

from src.models import ConfigError, RuleMatch
from src.preprocessing import tokenize


def _has_token_sequence(tokens: list[str], pattern_tokens: list[str]) -> bool:
    """Kiểm tra pattern_tokens có xuất hiện liền kề trong tokens hay không."""
    n = len(pattern_tokens)
    if n == 0 or n > len(tokens):
        return False
    if n == 1:
        return pattern_tokens[0] in tokens
    for i in range(len(tokens) - n + 1):
        if tokens[i : i + n] == pattern_tokens:
            return True
    return False


def load_rules(config_path: str = "config/rules.json") -> list[dict]:
    """Đọc và kiểm tra tính hợp lệ của tệp cấu hình quy tắc JSON."""
    path = Path(config_path)
    if not path.is_file():
        raise ConfigError(f"Không tìm thấy tệp cấu hình quy tắc: {config_path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Tệp '{config_path}' không đúng cú pháp JSON: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Không thể đọc tệp '{config_path}': {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("rules"), list) or not data["rules"]:
        raise ConfigError(f"Tệp '{config_path}' phải chứa danh sách 'rules' không rỗng.")

    seen_ids: set[str] = set()
    validated: list[dict] = []

    for idx, item in enumerate(data["rules"], start=1):
        if not isinstance(item, dict):
            raise ConfigError(f"Quy tắc thứ {idx} trong '{config_path}' phải là JSON object.")

        rule_id = item.get("id")
        pattern = item.get("pattern")
        weight = item.get("weight")
        description = item.get("description", "")

        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ConfigError(f"Quy tắc thứ {idx} thiếu trường 'id' hợp lệ.")
        if rule_id in seen_ids:
            raise ConfigError(f"Trùng mã quy tắc '{rule_id}' trong '{config_path}'.")
        if not isinstance(pattern, str) or not tokenize(pattern):
            raise ConfigError(f"Quy tắc '{rule_id}' có 'pattern' rỗng hoặc không hợp lệ.")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight == 0:
            raise ConfigError(f"Quy tắc '{rule_id}' phải có 'weight' là số khác 0.")
        if not isinstance(description, str):
            raise ConfigError(f"Quy tắc '{rule_id}' có 'description' không phải chuỗi.")

        seen_ids.add(rule_id)
        validated.append({
            "id": rule_id.strip(),
            "pattern": pattern.strip(),
            "weight": float(weight),
            "description": description.strip(),
        })

    return validated


def score_rules(
    tokens: list[str],
    rules: list[dict],
    min_score: float = -5.0,
    max_score: float = 5.0,
) -> tuple[float, list[RuleMatch]]:
    """Chấm điểm quy tắc theo ranh giới token; mỗi quy tắc tính tối đa 1 lần, chặn [-5, +5]."""
    raw_score = 0.0
    matched: list[RuleMatch] = []

    for rule in rules:
        pattern_tokens = tokenize(rule["pattern"])
        if _has_token_sequence(tokens, pattern_tokens):
            weight = float(rule["weight"])
            raw_score += weight
            matched.append(
                RuleMatch(
                    rule_id=rule["id"],
                    pattern=rule["pattern"],
                    weight=weight,
                    description=rule.get("description", ""),
                )
            )

    clamped = max(min_score, min(max_score, raw_score))
    return round(clamped, 4), matched
