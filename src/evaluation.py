"""Evaluation metrics, leakage checks, and reporting helpers for Email Spam Filter."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.models import Email
from src.preprocessing import normalize_text


def evaluate(y_true: list[str], y_pred: list[str]) -> dict:
    """Tính TP/TN/FP/FN, Accuracy, Precision, Recall, F1, FPR (spam = lớp dương)."""
    if len(y_true) != len(y_pred):
        raise ValueError("Độ dài y_true và y_pred phải bằng nhau.")

    tp = tn = fp = fn = 0
    for truth, pred in zip(y_true, y_pred):
        t = str(truth).strip().lower()
        p = str(pred).strip().lower()
        if t not in ("spam", "ham") or p not in ("spam", "ham"):
            raise ValueError(f"Nhãn không hợp lệ: truth='{truth}', pred='{pred}'.")
        if t == "spam" and p == "spam":
            tp += 1
        elif t == "ham" and p == "ham":
            tn += 1
        elif t == "ham" and p == "spam":
            fp += 1
        else:
            fn += 1

    total = tp + tn + fp + fn
    warnings: list[str] = []

    def _safe_div(num: float, den: float, name: str) -> float:
        if den == 0:
            warnings.append(f"{name} không xác định do mẫu số bằng 0 (trả về 0.0).")
            return 0.0
        return num / den

    accuracy = _safe_div(tp + tn, total, "Accuracy")
    precision = _safe_div(tp, tp + fp, "Precision")
    recall = _safe_div(tp, tp + fn, "Recall")
    f1 = _safe_div(2 * precision * recall, precision + recall, "F1")
    fpr = _safe_div(fp, fp + tn, "FPR")

    return {
        "total": total,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "warnings": warnings,
    }


def evaluate_majority_baseline(train_labels: list[str], test_labels: list[str]) -> dict:
    """Baseline luôn đoán nhãn phổ biến nhất trên tập train (hòa chọn 'ham')."""
    counts = Counter(str(lbl).strip().lower() for lbl in train_labels)
    majority_label = "spam" if counts["spam"] > counts["ham"] else "ham"
    preds = [majority_label] * len(test_labels)
    result = evaluate(test_labels, preds)
    result["baseline_label"] = majority_label
    return result


def check_data_leakage(
    train_emails: list[Email],
    val_emails: list[Email],
    test_emails: list[Email],
) -> dict:
    """Kiểm tra trùng lặp nội dung đã chuẩn hóa xuyên giữa train, validation và test."""
    def _index(emails: list[Email]) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for em in emails:
            key = normalize_text(f"{em.subject} {em.body}")
            mapping.setdefault(key, []).append(em.email_id)
        return mapping

    idx_train = _index(train_emails)
    idx_val = _index(val_emails)
    idx_test = _index(test_emails)

    pairs = {
        "train_val": set(idx_train) & set(idx_val),
        "train_test": set(idx_train) & set(idx_test),
        "val_test": set(idx_val) & set(idx_test),
    }

    overlap_counts = {name: len(keys) for name, keys in pairs.items()}
    overlap_ids = {
        "train_val": [(idx_train[k], idx_val[k]) for k in sorted(pairs["train_val"])],
        "train_test": [(idx_train[k], idx_test[k]) for k in sorted(pairs["train_test"])],
        "val_test": [(idx_val[k], idx_test[k]) for k in sorted(pairs["val_test"])],
    }
    return {
        "has_leakage": any(c > 0 for c in overlap_counts.values()),
        "overlap_counts": overlap_counts,
        "overlap_ids": overlap_ids,
    }


def export_evaluation_json(report: dict, output_path: str = "outputs/evaluation_report.json") -> str:
    """Xuất báo cáo đánh giá ra tệp JSON (UTF-8)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
