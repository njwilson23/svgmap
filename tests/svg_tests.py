import unittest
from worldly import svg
from util import xml_equal

class SVGOutputTests(unittest.TestCase):

    def test_circle(self):
        svg_circle = svg.SVGCircle((1, 3), 5)
        self.assertTrue(xml_equal('<circle cx="1" cy="3" r="5" />', str(svg_circle)))

    def test_polygon(self):
        svg_poly = svg.SVGPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertTrue(xml_equal('<polygon points="0,0 1,0 1,1 0,1" />', str(svg_poly)))

    def test_single_vertex_path(self):
        svg_path = svg.SVGPath([[(1, 2)]], closed=True)
        self.assertTrue(xml_equal('<path d="M1,2 Z" />', str(svg_path)))

    def test_multiple_path(self):
        svg_path = svg.SVGPath([[(0, -1), (1, -1), (1, 0), (0, 0)],
                                [(0, 0), (1, 0), (1, 1), (0, 1)]], closed=False)
        self.assertTrue(xml_equal('<path d="M0,-1 L1,-1 L1,0 L0,0 M0,0 L1,0 L1,1 L0,1" />',
                        str(svg_path)))

    def test_open_path(self):
        svg_path = svg.SVGPath([[(0, 0), (1, 0), (1, 1), (0, 1)]], closed=False)
        self.assertTrue(xml_equal('<path d="M0,0 L1,0 L1,1 L0,1" />', str(svg_path)))

    def test_closed_path(self):
        svg_path = svg.SVGPath([[(0, 0), (1, 0), (1, 1), (0, 1)]], closed=True)
        self.assertTrue(xml_equal('<path d="M0,0 L1,0 L1,1 L0,1 Z" />', str(svg_path)))

if __name__ == "__main__":
    unittest.main()
