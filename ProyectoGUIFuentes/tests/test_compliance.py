from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import sys
import unittest

SOURCE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_DIR))

from compliance import evaluate_compliance
from mpl_parser import MinPolInstance
from result_parser import MinPolResult


class ComplianceTests(unittest.TestCase):
    def setUp(self):
        self.instance = MinPolInstance(
            n=4,
            m=3,
            p=(2, 0, 2),
            v=(Decimal("0"), Decimal("0.5"), Decimal("1")),
            ce=(Decimal("0"), Decimal("0"), Decimal("0")),
            ct=Decimal("3"),
            max_movs=3,
            c=(
                (Decimal("0"), Decimal("1"), Decimal("3")),
                (Decimal("1"), Decimal("0"), Decimal("1")),
                (Decimal("3"), Decimal("1"), Decimal("0")),
            ),
        )

    def test_accepts_a_valid_optimal_solution(self):
        result = MinPolResult(
            movements=((0, 1, 0), (0, 0, 0), (0, 1, 0)),
            final_distribution=(1, 2, 1),
            total_cost=Fraction(3),
            total_movements=2,
            polarization=Fraction(1),
            median_index=2,
            median_value=Fraction(1, 2),
        )

        checks = evaluate_compliance(self.instance, result)

        self.assertEqual(len(checks), 7)
        self.assertTrue(all(check.passed for check in checks))

    def test_detects_budget_and_balance_violations(self):
        result = MinPolResult(
            movements=((0, 2, 0), (0, 0, 0), (0, 2, 0)),
            final_distribution=(2, 4, 2),
            total_cost=Fraction(6),
            total_movements=4,
            polarization=Fraction(2),
            median_index=2,
            median_value=Fraction(1, 2),
        )

        checks = {check.name: check for check in evaluate_compliance(
            self.instance, result
        )}

        self.assertFalse(checks["Balance poblacional"].passed)
        self.assertFalse(checks["Presupuesto"].passed)
        self.assertFalse(checks["Límite de movimientos"].passed)


if __name__ == "__main__":
    unittest.main()
