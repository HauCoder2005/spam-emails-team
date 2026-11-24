"""Unit tests verifying all shared core modules in src/."""

import unittest

from src.classifier import classify_email
from src.evaluation import check_data_leakage, evaluate, evaluate_majority_baseline
from src.models import DataLoadError, Email, ModelNotReadyError
from src.preprocessing import filter_stat_tokens, split_subject_body, tokenize
from src.rules import score_rules
from src.statistics import score_statistics, train_statistics


class TestCoreModules(unittest.TestCase):
    def test_preprocessing_and_split(self):
        subj, body = split_subject_body("Subject: WINNER!!!\r\nClaim your prize now.")
        self.assertEqual(subj, "WINNER!!!")
        self.assertEqual(body, "Claim your prize now.")
        # T01: case insensitive
        self.assertEqual(tokenize("WINNER!!!"), tokenize("winner"))
        tokens = tokenize("WINNER!!! Claim your prize now.")
        self.assertEqual(tokens, ["winner", "claim", "your", "prize", "now"])
        stat_tokens = filter_stat_tokens(tokens)
        self.assertNotIn("your", stat_tokens)
        self.assertIn("winner", stat_tokens)

    def test_rules_scoring_edge_cases(self):
        rules = [
            {"id": "R1", "pattern": "free", "weight": 2.0, "description": ""},
            {"id": "R2", "pattern": "claim your prize", "weight": 4.0, "description": ""},
            {"id": "R3", "pattern": "meeting agenda", "weight": -2.0, "description": ""},
        ]
        # T02: no substring match ('free' must not match 'freedom')
        score, matched = score_rules(tokenize("freedom for all"), rules)
        self.assertEqual(score, 0.0)
        self.assertEqual(matched, [])

        # T03: repeated word triggers rule only once
        score, matched = score_rules(tokenize("free free free"), rules)
        self.assertEqual(score, 2.0)
        self.assertEqual(len(matched), 1)

        # Clamping to +5 while keeping all matched rules
        score, matched = score_rules(tokenize("free claim your prize"), rules)
        self.assertEqual(score, 5.0)
        self.assertEqual(len(matched), 2)

        # T04: positive + negative signals
        score, matched = score_rules(tokenize("free meeting agenda"), rules)
        self.assertEqual(score, 0.0)
        self.assertEqual(len(matched), 2)

    def test_statistics_scoring_and_training(self):
        # Hand-calculated example from 02_GIAI_THICH_THUAT_TOAN.md: (2/5)*(2.0+1.5+1.1) = 1.84
        mock_model = {"weights": {"a": 2.0, "b": 1.5, "c": 1.1}}
        # T05: unseen word 'unknown' has weight 0 and does not raise error
        score, top_kw = score_statistics(["a", "b", "c", "unknown"], mock_model)
        self.assertAlmostEqual(score, 1.84, places=4)
        self.assertEqual(len(top_kw), 3)

        # T11: deterministic alphabetical tie-break on equal |W|
        tie_model = {"weights": {k: 1.0 for k in ["zeta", "alpha", "beta", "gamma", "delta", "epsilon"]}}
        _, top_tie = score_statistics(list(tie_model["weights"].keys()), tie_model, top_k=5)
        self.assertEqual([k.token for k in top_tie], ["alpha", "beta", "delta", "epsilon", "gamma"])

        # Training document frequency (min_df=3)
        train_emails = [
            Email(f"S{i}", "winner prize", "winner winner cash", label="spam") for i in range(4)
        ] + [
            Email(f"H{i}", "meeting agenda", "project report", label="ham") for i in range(4)
        ]
        model = train_statistics(train_emails, min_df=3)
        self.assertGreater(model["weights"]["winner"], 0.0)
        self.assertLess(model["weights"]["meeting"], 0.0)

    def test_evaluation_and_leakage(self):
        # Hand-calculated example: TP=32, TN=34, FP=3, FN=6
        y_true = ["spam"] * 38 + ["ham"] * 37
        y_pred = ["spam"] * 32 + ["ham"] * 6 + ["spam"] * 3 + ["ham"] * 34
        res = evaluate(y_true, y_pred)
        self.assertEqual((res["tp"], res["tn"], res["fp"], res["fn"]), (32, 34, 3, 6))
        self.assertAlmostEqual(res["accuracy"], 0.88, places=4)
        self.assertAlmostEqual(res["precision"], 32 / 35, places=4)
        self.assertAlmostEqual(res["recall"], 32 / 38, places=4)

        # T12: zero division safe handling
        zero_res = evaluate(["ham", "ham"], ["ham", "ham"])
        self.assertEqual(zero_res["precision"], 0.0)
        self.assertTrue(len(zero_res["warnings"]) > 0)

        # Baseline
        base = evaluate_majority_baseline(["ham", "ham", "spam"], ["spam", "ham"])
        self.assertEqual(base["baseline_label"], "ham")

        # T13: data leakage detection
        e1 = Email("E1", "Hello", "Meeting at 10")
        e2 = Email("E2", "HELLO!!!", "meeting at 10.")
        leak = check_data_leakage([e1], [], [e2])
        self.assertTrue(leak["has_leakage"])
        self.assertEqual(leak["overlap_counts"]["train_test"], 1)

    def test_hybrid_classifier(self):
        rules = [{"id": "R1", "pattern": "winner", "weight": 3.0, "description": ""}]
        stats_model = {"weights": {"prize": 2.0}}
        settings = {"thresholds": {"rule_only": 2.0, "statistics_only": 0.5, "combined": 1.0}}

        em = Email("E1", "Winner!", "Claim prize today")
        res = classify_email(em, "combined", rules, stats_model, settings)
        self.assertEqual(res.prediction, "spam")
        self.assertAlmostEqual(res.total_score, 3.8, places=4)

        # T06: empty email raises DataLoadError
        with self.assertRaises(DataLoadError):
            classify_email(Email("E0", "  ", ""), "rule_only", rules, None, settings)

        # T10: missing stats_model raises ModelNotReadyError
        with self.assertRaises(ModelNotReadyError):
            classify_email(em, "combined", rules, None, settings)


if __name__ == "__main__":
    unittest.main()
