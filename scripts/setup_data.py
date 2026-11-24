#!/usr/bin/env python3
"""Automated dataset download, validation, preprocessing, and splitting script.

Usage:
    python scripts/setup_data.py                  # Full idempotent setup
    python scripts/setup_data.py --download-only  # Only download & verify raw CSV
    python scripts/setup_data.py --verify         # Verify raw & processed datasets
    python scripts/setup_data.py --force          # Force re-download & regenerate all
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import shutil
import sys
from pathlib import Path
from typing import Callable, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing import (  # noqa: E402
    filter_stat_tokens,
    split_subject_body,
    tokenize,
)

# Increase CSV field size limit safely for long email bodies
try:
    csv.field_size_limit(min(sys.maxsize, 10 * 1024 * 1024))
except OverflowError:
    csv.field_size_limit(10 * 1024 * 1024)


class DataSetupError(Exception):
    """Raised when dataset download, validation, or preprocessing fails."""


class Logger:
    """Cross-platform colored console logger with step indicators."""

    COLORS = {
        "INFO": "\033[94m",
        "OK": "\033[92m",
        "WARN": "\033[93m",
        "ERR": "\033[91m",
        "STEP": "\033[96m",
        "RESET": "\033[0m",
    }

    def __init__(self, use_color: Optional[bool] = None) -> None:
        if use_color is None:
            self.use_color = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
        else:
            self.use_color = use_color
        # Ensure UTF-8 output on Windows consoles where possible
        for stream in (sys.stdout, sys.stderr):
            reconfigure = getattr(stream, "reconfigure", None)
            if callable(reconfigure):
                try:
                    reconfigure(encoding="utf-8", errors="replace")
                except Exception:
                    pass

    def _fmt(self, level: str, msg: str) -> str:
        if self.use_color:
            return f"{self.COLORS[level]}[{level}]{self.COLORS['RESET']} {msg}"
        return f"[{level}] {msg}"

    def info(self, msg: str) -> None:
        print(self._fmt("INFO", msg))

    def ok(self, msg: str) -> None:
        print(self._fmt("OK", msg))

    def warn(self, msg: str) -> None:
        print(self._fmt("WARN", msg))

    def step(self, msg: str) -> None:
        print(self._fmt("STEP", msg))

    def err(self, msg: str) -> None:
        print(self._fmt("ERR", msg), file=sys.stderr)


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest(project_root: Path) -> dict:
    """Load data/manifest.json from project_root."""
    manifest_path = project_root / "data" / "manifest.json"
    if not manifest_path.is_file():
        raise DataSetupError(f"Không tìm thấy tệp manifest: {manifest_path}")
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise DataSetupError(f"Lỗi đọc tệp manifest '{manifest_path}': {exc}") from exc


def ensure_directories(project_root: Path) -> None:
    """Create required data directories if they do not exist."""
    for rel in ("data", "data/raw", "data/processed", "outputs", "outputs/figures"):
        (project_root / rel).mkdir(parents=True, exist_ok=True)


def download_from_kaggle(
    handle: str,
    raw_filename: str,
    dest_path: Path,
    log: Logger,
    force_download: bool = False,
) -> Path:
    """Download pinned dataset version via kagglehub and copy target CSV to dest_path."""
    try:
        import kagglehub  # type: ignore
    except ImportError as exc:
        raise DataSetupError(
            "Chưa cài đặt thư viện 'kagglehub'. Hãy chạy: pip install -r requirements.txt"
        ) from exc

    log.step(f"Đang tải dataset Kaggle ({handle}) bằng kagglehub...")
    try:
        try:
            downloaded_dir = kagglehub.dataset_download(
                handle, force_download=force_download
            )
        except TypeError:
            # Older kagglehub versions may not accept force_download kwarg
            downloaded_dir = kagglehub.dataset_download(handle)
    except Exception as exc:
        raise DataSetupError(
            f"Tải dataset từ Kaggle thất bại ({type(exc).__name__}: {exc}). "
            "Vui lòng kiểm tra kết nối Internet hoặc cấu hình xác thực Kaggle API."
        ) from exc

    downloaded_path = Path(downloaded_dir)
    if not downloaded_path.exists():
        raise DataSetupError(f"Thư mục tải về từ kagglehub không tồn tại: {downloaded_path}")

    matches = [p for p in downloaded_path.rglob(raw_filename) if p.is_file()]
    if not matches:
        raise DataSetupError(
            f"Không tìm thấy tệp '{raw_filename}' trong thư mục tải về: {downloaded_path}"
        )

    source_csv = matches[0]
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dest_path.with_suffix(".csv.tmp")
    try:
        shutil.copy2(source_csv, tmp_path)
        tmp_path.replace(dest_path)
    except OSError as exc:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise DataSetupError(
            f"Không thể sao chép dataset vào '{dest_path}' (kiểm tra quyền ghi): {exc}"
        ) from exc

    log.ok(f"Đã sao chép raw dataset vào: {dest_path}")
    return dest_path


def validate_raw_dataset(
    raw_path: Path,
    manifest: dict,
    check_sha256: bool = True,
) -> dict:
    """Validate raw CSV existence, schema, row count, labels, NULLs, and SHA-256."""
    if not raw_path.is_file():
        raise DataSetupError(f"Thiếu raw dataset: {raw_path}")

    schema = manifest["expected_raw_schema"]
    required_cols = set(schema["required_columns"])
    allowed_labels = set(schema["allowed_labels"])
    allowed_nums = set(schema["allowed_label_nums"])
    expected_rows = manifest.get("expected_raw_rows")

    total_rows = 0
    label_counts = {"ham": 0, "spam": 0}

    try:
        with raw_path.open("r", encoding="utf-8", errors="strict", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise DataSetupError(f"Raw dataset '{raw_path}' bị rỗng hoặc thiếu tiêu đề cột.")

            if len(reader.fieldnames) > 50:
                raise DataSetupError(
                    f"Raw dataset '{raw_path}' có {len(reader.fieldnames)} cột (có vẻ là bảng "
                    "Bag-of-Words như emails.csv). Phải dùng spam_ham_dataset.csv nguyên văn."
                )

            missing_cols = required_cols - set(reader.fieldnames)
            if missing_cols:
                raise DataSetupError(
                    f"Raw dataset '{raw_path}' thiếu cột bắt buộc: {', '.join(sorted(missing_cols))}"
                )

            for row_idx, row in enumerate(reader, start=2):
                total_rows += 1
                text = row.get("text")
                label = (row.get("label") or "").strip().lower()
                label_num = (row.get("label_num") or "").strip()

                if text is None or not text.strip():
                    raise DataSetupError(f"Dòng {row_idx} trong '{raw_path}' có cột 'text' rỗng/NULL.")
                if label not in allowed_labels:
                    raise DataSetupError(
                        f"Dòng {row_idx} trong '{raw_path}' có nhãn 'label' không hợp lệ: '{label}'."
                    )
                if label_num not in allowed_nums:
                    raise DataSetupError(
                        f"Dòng {row_idx} trong '{raw_path}' có 'label_num' không hợp lệ: '{label_num}'."
                    )
                expected_num = "1" if label == "spam" else "0"
                if label_num != expected_num:
                    raise DataSetupError(
                        f"Dòng {row_idx} trong '{raw_path}' bị lệch nhãn: "
                        f"label='{label}' nhưng label_num='{label_num}'."
                    )
                label_counts[label] += 1
    except UnicodeDecodeError as exc:
        raise DataSetupError(f"Lỗi encoding UTF-8 khi đọc '{raw_path}': {exc}") from exc
    except OSError as exc:
        raise DataSetupError(f"Không thể đọc tệp '{raw_path}': {exc}") from exc

    if expected_rows is not None and total_rows != expected_rows:
        raise DataSetupError(
            f"Raw dataset '{raw_path}' có {total_rows} dòng, không khớp kỳ vọng {expected_rows} dòng."
        )

    sha256 = compute_sha256(raw_path)
    expected_sha256 = manifest.get("raw_sha256")
    if check_sha256 and expected_sha256 and sha256 != expected_sha256:
        raise DataSetupError(
            f"SHA-256 của '{raw_path}' không khớp manifest!\n"
            f"  Thực tế : {sha256}\n"
            f"  Kỳ vọng : {expected_sha256}"
        )

    return {
        "path": str(raw_path),
        "rows": total_rows,
        "label_counts": label_counts,
        "sha256": sha256,
    }


def _write_csv_atomic(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    """Write CSV atomically via a temporary file so partial writes never corrupt data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".csv.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        tmp_path.replace(path)
    except OSError as exc:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise DataSetupError(f"Không thể ghi tệp '{path}': {exc}") from exc


def build_processed_datasets(
    project_root: Path,
    raw_path: Path,
    manifest: dict,
    log: Logger,
    force: bool = False,
) -> dict:
    """Preprocess raw dataset, deduplicate before split, and write train/val/test/unlabeled CSVs."""
    # 1. Ensure validated copy in data/processed/spam_ham_dataset.csv
    processed_raw_copy = project_root / "data" / "processed" / manifest["raw_filename"]
    if force or not processed_raw_copy.is_file():
        tmp_copy = processed_raw_copy.with_suffix(".csv.tmp")
        try:
            shutil.copy2(raw_path, tmp_copy)
            tmp_copy.replace(processed_raw_copy)
        except OSError as exc:
            if tmp_copy.exists():
                tmp_copy.unlink(missing_ok=True)
            raise DataSetupError(
                f"Không thể đồng bộ bản sao tới '{processed_raw_copy}': {exc}"
            ) from exc

    # 2. Read, clean, tokenize using shared src/preprocessing.py, and deduplicate BEFORE split
    seen_clean: set[str] = set()
    spam_pool: list[dict] = []
    ham_pool: list[dict] = []
    dropped_empty = 0
    dropped_duplicates = 0

    with raw_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            raw_text = row["text"]
            label = row["label"].strip().lower()
            label_num = 1 if label == "spam" else 0

            subject, body = split_subject_body(raw_text)
            rule_tokens = tokenize(f"{subject} {body}")
            clean_text = " ".join(rule_tokens)
            if not clean_text:
                dropped_empty += 1
                continue

            if clean_text in seen_clean:
                dropped_duplicates += 1
                continue
            seen_clean.add(clean_text)

            stat_text = " ".join(filter_stat_tokens(rule_tokens))
            record = {
                "subject": subject,
                "body": body,
                "clean_text": clean_text,
                "stat_text": stat_text,
                "label": label,
                "label_num": label_num,
            }
            if label == "spam":
                spam_pool.append(record)
            else:
                ham_pool.append(record)

    split_cfg = manifest["split_config"]
    need_spam = split_cfg["per_class_samples"]["spam"]
    need_ham = split_cfg["per_class_samples"]["ham"]
    need_unlabeled = split_cfg["unlabeled_sample"]["total"]
    unlabeled_spam_n = need_unlabeled // 2
    unlabeled_ham_n = need_unlabeled - unlabeled_spam_n

    if len(spam_pool) < need_spam + unlabeled_spam_n:
        raise DataSetupError(
            f"Không đủ email spam duy nhất ({len(spam_pool)} < {need_spam + unlabeled_spam_n})."
        )
    if len(ham_pool) < need_ham + unlabeled_ham_n:
        raise DataSetupError(
            f"Không đủ email ham duy nhất ({len(ham_pool)} < {need_ham + unlabeled_ham_n})."
        )

    rng = random.Random(manifest["random_seed"])
    rng.shuffle(spam_pool)
    rng.shuffle(ham_pool)

    # Slice disjoint partitions
    splits_cfg = split_cfg["splits"]
    s_tr, h_tr = splits_cfg["train"]["spam"], splits_cfg["train"]["ham"]
    s_va, h_va = splits_cfg["validation"]["spam"], splits_cfg["validation"]["ham"]
    s_te, h_te = splits_cfg["test"]["spam"], splits_cfg["test"]["ham"]

    train_rows = spam_pool[:s_tr] + ham_pool[:h_tr]
    val_rows = spam_pool[s_tr : s_tr + s_va] + ham_pool[h_tr : h_tr + h_va]
    test_rows = (
        spam_pool[s_tr + s_va : s_tr + s_va + s_te]
        + ham_pool[h_tr + h_va : h_tr + h_va + h_te]
    )
    unlabeled_rows = (
        spam_pool[need_spam : need_spam + unlabeled_spam_n]
        + ham_pool[need_ham : need_ham + unlabeled_ham_n]
    )

    rng.shuffle(train_rows)
    rng.shuffle(val_rows)
    rng.shuffle(test_rows)
    rng.shuffle(unlabeled_rows)

    # Assign deterministic IDs
    labeled_cols = manifest["expected_output_schema"]["labeled_columns"]
    unlabeled_cols = manifest["expected_output_schema"]["unlabeled_columns"]

    counter = 1
    for group in (train_rows, val_rows, test_rows):
        for rec in group:
            rec["email_id"] = f"E{counter:04d}"
            counter += 1

    unlabeled_out: list[dict] = []
    for idx, rec in enumerate(unlabeled_rows, start=1):
        unlabeled_out.append({
            "email_id": f"U{idx:03d}",
            "subject": rec["subject"],
            "body": rec["body"],
            "clean_text": rec["clean_text"],
            "stat_text": rec["stat_text"],
        })

    # Verify 0 data leakage before writing
    sets = {
        "train": {r["clean_text"] for r in train_rows},
        "validation": {r["clean_text"] for r in val_rows},
        "test": {r["clean_text"] for r in test_rows},
        "unlabeled": {r["clean_text"] for r in unlabeled_out},
    }
    names = list(sets.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            overlap = sets[names[i]] & sets[names[j]]
            if overlap:
                raise DataSetupError(
                    f"Phát hiện rò rỉ dữ liệu ({len(overlap)} bản ghi trùng) giữa {names[i]} và {names[j]}."
                )

    _write_csv_atomic(project_root / splits_cfg["train"]["path"], labeled_cols, train_rows)
    _write_csv_atomic(project_root / splits_cfg["validation"]["path"], labeled_cols, val_rows)
    _write_csv_atomic(project_root / splits_cfg["test"]["path"], labeled_cols, test_rows)
    _write_csv_atomic(
        project_root / split_cfg["unlabeled_sample"]["path"], unlabeled_cols, unlabeled_out
    )

    log.ok(
        f"Đã sinh dữ liệu sạch (bỏ {dropped_empty} rỗng, {dropped_duplicates} trùng lặp): "
        f"train={len(train_rows)}, validation={len(val_rows)}, test={len(test_rows)}, "
        f"unlabeled={len(unlabeled_out)} (0 data leakage)."
    )
    return {
        "dropped_empty": dropped_empty,
        "dropped_duplicates": dropped_duplicates,
        "train": len(train_rows),
        "validation": len(val_rows),
        "test": len(test_rows),
        "unlabeled": len(unlabeled_out),
    }


def verify_processed_datasets(project_root: Path, manifest: dict) -> dict:
    """Verify all expected processed output CSVs exist, match schema/counts, and have 0 leakage."""
    for rel in manifest["expected_output_files"]:
        full_path = project_root / rel
        if not full_path.is_file():
            raise DataSetupError(f"Thiếu tệp dữ liệu đã xử lý: {rel}")

    # Validate processed raw copy
    processed_raw_copy = project_root / "data" / "processed" / manifest["raw_filename"]
    validate_raw_dataset(processed_raw_copy, manifest, check_sha256=True)

    labeled_cols = manifest["expected_output_schema"]["labeled_columns"]
    unlabeled_cols = manifest["expected_output_schema"]["unlabeled_columns"]
    splits_cfg = manifest["split_config"]["splits"]

    clean_sets: dict[str, set[str]] = {}
    summary: dict[str, dict] = {}

    for split_name in ("train", "validation", "test"):
        spec = splits_cfg[split_name]
        csv_path = project_root / spec["path"]
        counts = {"spam": 0, "ham": 0}
        clean_set: set[str] = set()

        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != labeled_cols:
                raise DataSetupError(
                    f"Tệp '{spec['path']}' sai schema cột: {reader.fieldnames} != {labeled_cols}"
                )
            for row_idx, row in enumerate(reader, start=2):
                lbl = (row.get("label") or "").strip().lower()
                lbl_num = (row.get("label_num") or "").strip()
                clean = (row.get("clean_text") or "").strip()
                if lbl not in ("spam", "ham") or lbl_num != ("1" if lbl == "spam" else "0"):
                    raise DataSetupError(f"Dòng {row_idx} trong '{spec['path']}' sai nhãn.")
                if not clean:
                    raise DataSetupError(f"Dòng {row_idx} trong '{spec['path']}' có clean_text rỗng.")
                counts[lbl] += 1
                clean_set.add(clean)

        total = counts["spam"] + counts["ham"]
        if total != spec["total"] or counts["spam"] != spec["spam"] or counts["ham"] != spec["ham"]:
            raise DataSetupError(
                f"Tệp '{spec['path']}' sai phân bố số lượng: {counts} "
                f"(kỳ vọng spam={spec['spam']}, ham={spec['ham']})."
            )
        clean_sets[split_name] = clean_set
        summary[split_name] = {"total": total, **counts}

    # Verify unlabeled_sample.csv
    unlabeled_spec = manifest["split_config"]["unlabeled_sample"]
    unlabeled_path = project_root / unlabeled_spec["path"]
    unlabeled_clean: set[str] = set()
    unlabeled_count = 0
    with unlabeled_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != unlabeled_cols:
            raise DataSetupError(
                f"Tệp '{unlabeled_spec['path']}' sai schema cột: {reader.fieldnames} != {unlabeled_cols}"
            )
        for row_idx, row in enumerate(reader, start=2):
            clean = (row.get("clean_text") or "").strip()
            if not clean:
                raise DataSetupError(f"Dòng {row_idx} trong '{unlabeled_spec['path']}' có clean_text rỗng.")
            unlabeled_clean.add(clean)
            unlabeled_count += 1

    if unlabeled_count != unlabeled_spec["total"]:
        raise DataSetupError(
            f"Tệp '{unlabeled_spec['path']}' có {unlabeled_count} dòng (kỳ vọng {unlabeled_spec['total']})."
        )
    clean_sets["unlabeled"] = unlabeled_clean
    summary["unlabeled"] = {"total": unlabeled_count}

    # Verify 0 leakage across all partitions
    names = list(clean_sets.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            overlap = clean_sets[names[i]] & clean_sets[names[j]]
            if overlap:
                raise DataSetupError(
                    f"Phát hiện rò rỉ dữ liệu ({len(overlap)} trùng lặp) giữa {names[i]} và {names[j]}."
                )

    return summary


def run_setup(
    project_root: Path = PROJECT_ROOT,
    download_only: bool = False,
    verify: bool = False,
    force: bool = False,
    downloader: Optional[Callable[[str, str, Path, Logger, bool], Path]] = None,
    log: Optional[Logger] = None,
) -> int:
    """Main orchestration entry point; returns POSIX exit code (0 = success, 1 = failure)."""
    logger = log or Logger()
    download_fn = downloader or download_from_kaggle

    try:
        manifest = load_manifest(project_root)
        raw_path = project_root / manifest["raw_path"]
        processed_raw_copy = project_root / "data" / "processed" / manifest["raw_filename"]

        if verify:
            logger.step("Kiểm tra tính hợp lệ của raw dataset và toàn bộ processed dataset...")
            raw_info = validate_raw_dataset(raw_path, manifest, check_sha256=True)
            logger.ok(
                f"Raw dataset hợp lệ: {raw_info['rows']} dòng "
                f"(ham={raw_info['label_counts']['ham']}, spam={raw_info['label_counts']['spam']})."
            )
            proc_info = verify_processed_datasets(project_root, manifest)
            logger.ok(f"Processed datasets hợp lệ & 0 data leakage: {proc_info}")
            return 0

        ensure_directories(project_root)

        # Step 1: Ensure raw dataset is present and valid
        raw_valid = False
        if not force and raw_path.is_file():
            try:
                raw_info = validate_raw_dataset(raw_path, manifest, check_sha256=True)
                raw_valid = True
                logger.info(
                    f"Raw dataset đã tồn tại và hợp lệ ({raw_info['rows']} dòng) — bỏ qua bước tải."
                )
            except DataSetupError as exc:
                raise DataSetupError(
                    f"Raw dataset hiện có không hợp lệ: {exc}\n"
                    "Nếu muốn tải lại từ đầu, hãy chạy: python scripts/setup_data.py --force"
                ) from exc

        if not raw_valid:
            if not force and processed_raw_copy.is_file():
                try:
                    validate_raw_dataset(processed_raw_copy, manifest, check_sha256=True)
                    logger.info(
                        f"Phát hiện dataset gốc hợp lệ tại '{processed_raw_copy}', "
                        f"đang sao chép sang '{raw_path}' (không cần tải lại)..."
                    )
                    tmp_path = raw_path.with_suffix(".csv.tmp")
                    shutil.copy2(processed_raw_copy, tmp_path)
                    tmp_path.replace(raw_path)
                    raw_valid = True
                except DataSetupError:
                    raw_valid = False

        if not raw_valid:
            download_fn(
                manifest["kagglehub_handle"],
                manifest["raw_filename"],
                raw_path,
                logger,
                force,
            )
            raw_info = validate_raw_dataset(raw_path, manifest, check_sha256=True)
            logger.ok(
                f"Xác thực raw dataset thành công: {raw_info['rows']} dòng "
                f"(SHA-256 khớp manifest)."
            )

        if download_only:
            logger.ok("Hoàn tất chế độ --download-only.")
            return 0

        # Step 2: Ensure processed datasets exist and are valid (idempotent)
        if not force:
            try:
                proc_info = verify_processed_datasets(project_root, manifest)
                logger.info(
                    f"Toàn bộ processed datasets đã tồn tại và hợp lệ ({proc_info}) — không ghi đè."
                )
                logger.ok("Setup dữ liệu hoàn tất (không có thay đổi cần thực hiện).")
                return 0
            except DataSetupError as exc:
                logger.warn(f"Cần tái tạo processed datasets ({exc}). Đang chạy tiền xử lý...")

        logger.step("Đang chạy tiền xử lý, khử trùng lặp và chia tập train/validation/test...")
        build_processed_datasets(project_root, raw_path, manifest, logger, force=force)
        verify_processed_datasets(project_root, manifest)
        logger.ok("Hoàn tất khởi tạo & xác thực toàn bộ dữ liệu dự án!")
        return 0

    except DataSetupError as exc:
        logger.err(str(exc))
        return 1
    except KeyboardInterrupt:
        logger.err("Người dùng đã hủy quá trình setup.")
        return 130
    except Exception as exc:
        logger.err(f"Lỗi không mong muốn trong quá trình setup ({type(exc).__name__}: {exc})")
        return 1


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tự động tải, kiểm tra và khởi tạo bộ dữ liệu Email Spam Detection."
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--download-only",
        action="store_true",
        help="Chỉ tải và xác thực raw dataset vào data/raw/.",
    )
    mode_group.add_argument(
        "--verify",
        action="store_true",
        help="Kiểm tra tính hợp lệ của raw và toàn bộ processed dataset hiện có.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Chủ động tải lại raw dataset và tái tạo toàn bộ processed datasets.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if args.verify and args.force:
        Logger().err("Không thể kết hợp --verify với --force.")
        return 2
    return run_setup(
        project_root=PROJECT_ROOT,
        download_only=args.download_only,
        verify=args.verify,
        force=args.force,
    )


if __name__ == "__main__":
    sys.exit(main())
