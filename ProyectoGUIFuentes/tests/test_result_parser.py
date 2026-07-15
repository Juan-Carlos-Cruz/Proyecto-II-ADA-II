from fractions import Fraction
from pathlib import Path
import sys
import unittest

SOURCE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_DIR))

from result_parser import parse_minizinc_output


OUTPUT = """\
%%%mzn-stat: nodes=225
MATRIZ_MOVIMIENTOS
0,0
1,0
DISTRIBUCION_FINAL=[2, 0]
COSTO_TOTAL=12/10
TOTAL_MOVIMIENTOS=1
MAX_MOVIMIENTOS=3
POLARIZACION=0/100
INDICE_MEDIANA=1
VALOR_MEDIANA=0/100
----------
==========
"""


class ResultParserTests(unittest.TestCase):
    def test_parses_labeled_output(self):
        result = parse_minizinc_output(OUTPUT, 2)
        self.assertEqual(result.movements, ((0, 0), (1, 0)))
        self.assertEqual(result.final_distribution, (2, 0))
        self.assertEqual(result.total_cost, Fraction(6, 5))
        self.assertEqual(result.total_movements, 1)
        self.assertEqual(result.polarization, Fraction(0))
        self.assertEqual(result.statistics["nodes"], "225")


if __name__ == "__main__":
    unittest.main()
