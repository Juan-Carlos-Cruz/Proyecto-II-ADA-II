from decimal import Decimal
from pathlib import Path
import sys
import unittest

SOURCE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_DIR))

from pca_parser import PCAValidationError, instance_to_dzn, parse_pca_text


VALID = """\
20
5
12,4,0,4,0
0,0.25,0.5,0.75,1
1,2,1,1,3
20
0,2,4,5,7
1,0,3,4,6
3,2,0,2,4
4,2,1,0,2
8,5,3,2,0
"""


class PCAParserTests(unittest.TestCase):
    def test_reads_pdf_example(self):
        instance = parse_pca_text(VALID)
        self.assertEqual(instance.n, 20)
        self.assertEqual(instance.m, 5)
        self.assertEqual(instance.p, (12, 4, 0, 4, 0))
        self.assertEqual(instance.v[1], Decimal("0.25"))

    def test_generates_exact_scales(self):
        dzn = instance_to_dzn(parse_pca_text(VALID))
        self.assertIn("escala_v = 100;", dzn)
        self.assertIn("v = [0, 25, 50, 75, 100];", dzn)
        self.assertIn("escala_costo = 1;", dzn)

    def test_rejects_wrong_population_sum(self):
        invalid = VALID.replace("12,4,0,4,0", "11,4,0,4,0")
        with self.assertRaisesRegex(PCAValidationError, "suma de p"):
            parse_pca_text(invalid)

    def test_rejects_missing_m_line(self):
        invalid = VALID.replace("20\n5\n", "20\n", 1)
        with self.assertRaises(PCAValidationError):
            parse_pca_text(invalid)

    def test_rejects_negative_cost(self):
        invalid = VALID.replace("8,5,3,2,0", "8,5,-3,2,0")
        with self.assertRaisesRegex(PCAValidationError, "no pueden ser negativos"):
            parse_pca_text(invalid)


if __name__ == "__main__":
    unittest.main()
