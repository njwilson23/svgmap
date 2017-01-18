import unittest
import io
import sys
sys.path.append(".")
from svgmap import svg, mapsheet

class MapSheetTests(unittest.TestCase):

    def test_simple_map(self):

        poly = svg.SVGPolygon([(100, 100), (400, 100), (400, 400), (100, 400)],
                              id_name="empty")

        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.style = "#empty { stroke: black; fill: red; }"
            sheet.add(poly)

        buf.seek(0)
        self.assertEqual(buf.read(),
            '<svg height="500" width="500" xmlns="http://www.w3.org/2000/svg"><polygon id="empty" points="100,100 400,100 400,400 100,400" /><style>#empty { stroke: black; fill: red; }</style></svg>')
        return


    def test_polygons_from_string(self):
        with open("tests/vancouver_island/vancouver_island.geojson") as f:
            s = f.read()

        buf = io.StringIO()
        with mapsheet.MapSheet(buf, bbox=(-129, 48, -123, 51)) as sheet:
            sheet.add(s)

        self.assertEqual(len(sheet.entities), 22)
        return

class SVGOutputTests(unittest.TestCase):

    def test_circle(self):
        svg_circle = svg.SVGCircle((1, 3), 5)
        self.assertEqual('<circle cx="1" cy="3" r="5" />', str(svg_circle))

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
