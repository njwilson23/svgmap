import unittest

import sys
sys.path.append(".")
from svgmap import svg, mapsheet

class MapSheetTests(unittest.TestCase):

    def test_simple_map(self):

        poly = svg.SVGPolygon([(100, 100), (400, 100), (400, 400), (100, 400)],
                              id_name="empty")

        with mapsheet.MapFile("map.svg") as mapfile:
            mapfile.mapsheet.style = "#empty { stroke: black; fill: red; }"
            mapfile.add(poly)


class SVGOutputTests(unittest.TestCase):

    def test_polygon(self):
        svg_poly = svg.SVGPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        out = str(svg_poly)
        self.assertEqual('<polygon points="0,0 1,0 1,1 0,1" />', out)

    def test_open_path(self):
        svg_path = svg.SVGPath([(0, 0), (1, 0), (1, 1), (0, 1)], closed=False)
        out = str(svg_path)
        self.assertEqual('<path d="M0,0 L1,0 L0,1 L-1,0" />', out)

    def test_closed_path(self):
        svg_path = svg.SVGPath([(0, 0), (1, 0), (1, 1), (0, 1)], closed=True)
        out = str(svg_path)
        self.assertEqual('<path d="M0,0 L1,0 L0,1 L-1,0 Z" />', out)

if __name__ == "__main__":
    unittest.main()
