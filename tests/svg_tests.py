import unittest

import sys
sys.path.append(".")
from svgmap import svg

class SVGOutputTests(unittest.TestCase):

    def test_polygon(self):
        svg_poly = svg.SVGPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        out = svg_poly.svg()
        self.assertEqual('<polygon points="0,0 1,0 1,1 0,1"/>', out)

    def test_open_path(self):
        svg_path = svg.SVGPath([(0, 0), (1, 0), (1, 1), (0, 1)], closed=False)
        out = svg_path.svg()
        self.assertEqual('<path d="M0,0 L1,0 L0,1 L-1,0"/>', out)

    def test_closed_path(self):
        svg_path = svg.SVGPath([(0, 0), (1, 0), (1, 1), (0, 1)], closed=True)
        out = svg_path.svg()
        self.assertEqual('<path d="M0,0 L1,0 L0,1 L-1,0 Z"/>', out)

if __name__ == "__main__":
    unittest.main()
