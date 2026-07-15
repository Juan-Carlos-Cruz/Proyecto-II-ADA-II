from decimal import Decimal
from pathlib import Path
import sys
import unittest

SOURCE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_DIR))

from mpl_parser import MPLValidationError, instance_to_dzn, parse_mpl_text


VALID = """\
20
5
12,4,0,4,0
0,0.25,0.5,0.75,1
1,2,1,1,3
0,2,4,5,7
1,0,3,4,6
3,2,0,2,4
4,2,1,0,2
8,5,3,2,0
20
18
"""


class MPLParserTests(unittest.TestCase):
    def test_reads_pdf_example(self):
        instance = parse_mpl_text(VALID)
        self.assertEqual(instance.n, 20)
        self.assertEqual(instance.m, 5)
        self.assertEqual(instance.p, (12, 4, 0, 4, 0))
        self.assertEqual(instance.v[1], Decimal("0.25"))
        self.assertEqual(instance.max_movs, 18)

    def test_generates_exact_scales(self):
        dzn = instance_to_dzn(parse_mpl_text(VALID))
        self.assertIn("escala_v = 100;", dzn)
        self.assertIn("v = [0, 25, 50, 75, 100];", dzn)
        self.assertIn("escala_costo = 1;", dzn)
        self.assertIn("maxM = 18;", dzn)

    def test_rejects_wrong_population_sum(self):
        invalid = VALID.replace("12,4,0,4,0", "11,4,0,4,0")
        with self.assertRaisesRegex(MPLValidationError, "suma de p"):
            parse_mpl_text(invalid)

    def test_rejects_missing_m_line(self):
        invalid = VALID.replace("20\n5\n", "20\n", 1)
        with self.assertRaises(MPLValidationError):
            parse_mpl_text(invalid)

    def test_rejects_negative_cost(self):
        invalid = VALID.replace("8,5,3,2,0", "8,5,-3,2,0")
        with self.assertRaisesRegex(MPLValidationError, "no pueden ser negativos"):
            parse_mpl_text(invalid)


if __name__ == "__main__":
    unittest.main()
