"""Comprehensive tests for scripts/setup_data.py covering all acceptance scenarios."""

from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.setup_data import (
    DataSetupError,
    Logger,
    compute_sha256,
    run_setup,
)


def _create_synthetic_raw_csv(path: Path, n_spam: int = 30, n_ham: int = 30) -> str:
    """Create a valid synthetic Kaggle-format CSV and return its SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    idx = 0
    for i in range(n_spam):
        rows.append({
            "": str(idx),
            "label": "spam",
            "text": f"Subject: Winner prize offer {i}\r\nClaim your free cash bonus number {i} now!",
            "label_num": "1",
        })
        idx += 1
    for i in range(n_ham):
        rows.append({
            "": str(idx),
            "label": "ham",
            "text": f"Subject: Meeting agenda {i}\r\nHi team please review project update {i} tomorrow.",
            "label_num": "0",
        })
        idx += 1
    # Add 2 intentional duplicate rows to verify deduplication before split
    rows.append(dict(rows[0], **{"": str(idx)}))
    rows.append(dict(rows[n_spam], **{"": str(idx + 1)}))

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["", "label", "text", "label_num"])
        writer.writeheader()
        writer.writerows(rows)
    return compute_sha256(path)


def _write_test_manifest(root: Path, raw_sha256: str, expected_raw_rows: int = 62) -> None:
    manifest = {
        "dataset_id": "venky73/spam-mails-dataset",
        "dataset_version": 1,
        "kagglehub_handle": "venky73/spam-mails-dataset/versions/1",
        "source_url": "https://www.kaggle.com/datasets/venky73/spam-mails-dataset",
        "raw_filename": "spam_ham_dataset.csv",
        "raw_path": "data/raw/spam_ham_dataset.csv",
        "raw_sha256": raw_sha256,
        "expected_raw_rows": expected_raw_rows,
        "expected_raw_schema": {
            "required_columns": ["text", "label", "label_num"],
            "allowed_labels": ["ham", "spam"],
            "allowed_label_nums": ["0", "1"],
        },
        "random_seed": 42,
        "split_config": {
            "total_labeled_samples": 40,
            "per_class_samples": {"spam": 20, "ham": 20},
            "splits": {
                "train": {"path": "data/train.csv", "total": 24, "spam": 12, "ham": 12},
                "validation": {"path": "data/validation.csv", "total": 8, "spam": 4, "ham": 4},
                "test": {"path": "data/test.csv", "total": 8, "spam": 4, "ham": 4},
            },
            "unlabeled_sample": {"path": "data/unlabeled_sample.csv", "total": 6},
        },
        "expected_output_schema": {
            "labeled_columns": [
                "email_id", "subject", "body", "clean_text", "stat_text", "label", "label_num"
            ],
            "unlabeled_columns": ["email_id", "subject", "body", "clean_text", "stat_text"],
        },
        "expected_output_files": [
            "data/processed/spam_ham_dataset.csv",
            "data/train.csv",
            "data/validation.csv",
            "data/test.csv",
            "data/unlabeled_sample.csv",
        ],
    }
    manifest_path = root / "data" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


class TestSetupData(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source_fixture = self.root / "_fixture_source.csv"
        self.sha256 = _create_synthetic_raw_csv(self.source_fixture)
        _write_test_manifest(self.root, self.sha256, expected_raw_rows=62)
        self.download_calls = 0
        self.log = Logger(use_color=False)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _mock_downloader(self, handle: str, raw_filename: str, dest: Path, log: Logger, force: bool) -> Path:
        self.download_calls += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.source_fixture, dest)
        return dest

    def _failing_downloader(self, handle: str, raw_filename: str, dest: Path, log: Logger, force: bool) -> Path:
        self.download_calls += 1
        raise DataSetupError("Mất kết nối Internet khi tải Kaggle dataset.")

    def test_1_fresh_clone_and_verify(self):
        code = run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log)
        self.assertEqual(code, 0)
        self.assertEqual(self.download_calls, 1)
        self.assertTrue((self.root / "data/raw/spam_ham_dataset.csv").is_file())
        self.assertTrue((self.root / "data/train.csv").is_file())
        self.assertTrue((self.root / "data/validation.csv").is_file())
        self.assertTrue((self.root / "data/test.csv").is_file())
        self.assertTrue((self.root / "data/unlabeled_sample.csv").is_file())

        # --verify passes on valid data
        vcode = run_setup(project_root=self.root, verify=True, log=self.log)
        self.assertEqual(vcode, 0)

    def test_2_existing_raw_skips_download(self):
        raw_path = self.root / "data/raw/spam_ham_dataset.csv"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.source_fixture, raw_path)

        code = run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log)
        self.assertEqual(code, 0)
        self.assertEqual(self.download_calls, 0)
        self.assertTrue((self.root / "data/train.csv").is_file())

    def test_3_idempotent_repeated_runs_no_overwrite(self):
        self.assertEqual(run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log), 0)
        train_path = self.root / "data/train.csv"
        first_bytes = train_path.read_bytes()
        first_mtime = train_path.stat().st_mtime_ns

        # Second run should neither re-download nor overwrite train.csv
        self.assertEqual(run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log), 0)
        self.assertEqual(self.download_calls, 1)
        self.assertEqual(train_path.stat().st_mtime_ns, first_mtime)
        self.assertEqual(train_path.read_bytes(), first_bytes)

    def test_4_missing_one_processed_file_regenerates(self):
        self.assertEqual(run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log), 0)
        test_csv = self.root / "data/test.csv"
        test_csv.unlink()

        # --verify must fail when test.csv is missing
        self.assertEqual(run_setup(project_root=self.root, verify=True, log=self.log), 1)

        # Re-running setup regenerates test.csv WITHOUT re-downloading raw
        self.assertEqual(run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log), 0)
        self.assertEqual(self.download_calls, 1)
        self.assertTrue(test_csv.is_file())
        self.assertEqual(run_setup(project_root=self.root, verify=True, log=self.log), 0)

    def test_5_invalid_schema_rejected(self):
        raw_path = self.root / "data/raw/spam_ham_dataset.csv"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        # Write a Bag-of-Words-like file missing required 'text' column
        raw_path.write_text("Email No.,the,to,Prediction\nEmail 1,0,1,0\n", encoding="utf-8")

        code = run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log)
        self.assertEqual(code, 1)
        self.assertEqual(run_setup(project_root=self.root, verify=True, log=self.log), 1)

    def test_6_download_failure_returns_nonzero(self):
        code = run_setup(project_root=self.root, downloader=self._failing_downloader, log=self.log)
        self.assertEqual(code, 1)
        self.assertEqual(self.download_calls, 1)
        self.assertFalse((self.root / "data/train.csv").exists())

    def test_7_force_redownloads_and_regenerates(self):
        self.assertEqual(run_setup(project_root=self.root, downloader=self._mock_downloader, log=self.log), 0)
        self.assertEqual(self.download_calls, 1)

        # --force must call downloader again and produce identical deterministic output
        train_before = (self.root / "data/train.csv").read_bytes()
        code = run_setup(
            project_root=self.root, force=True, downloader=self._mock_downloader, log=self.log
        )
        self.assertEqual(code, 0)
        self.assertEqual(self.download_calls, 2)
        self.assertEqual((self.root / "data/train.csv").read_bytes(), train_before)

    def test_8_download_only_mode(self):
        code = run_setup(
            project_root=self.root,
            download_only=True,
            downloader=self._mock_downloader,
            log=self.log,
        )
        self.assertEqual(code, 0)
        self.assertTrue((self.root / "data/raw/spam_ham_dataset.csv").is_file())
        self.assertFalse((self.root / "data/train.csv").exists())


if __name__ == "__main__":
    unittest.main()
