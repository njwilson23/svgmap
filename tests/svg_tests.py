import unittest
import io
import xml.etree.ElementTree as ET
from worldly import svg, mapsheet

def _xml_element_equal(el1, el2):
    if el1.tag != el2.tag:
        return False
    if el1.attrib != el2.attrib:
        return False
    children1 = el1.getchildren()
    children2 = el2.getchildren()
    if len(children1) != len(children2):
        return False
    for child1, child2 in zip(children1, children2):
        if not _xml_element_equal(child1, child2):
            return False
    return True

def xml_equal(str1, str2):
    et1 = ET.fromstring(str1)
    et2 = ET.fromstring(str2)
    return _xml_element_equal(et1, et2)

class MapSheetTests(unittest.TestCase):

    def test_simple_map(self):

        poly = svg.SVGPolygon([(100, 100), (400, 100), (400, 400), (100, 400)],
                              id_name="empty")

        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.style = "#empty { stroke: black; fill: red; }"
            sheet.add_svg(poly)

        buf.seek(0)
        self.assertTrue(xml_equal(buf.read(),
            '<svg height="500" width="500" xmlns="http://www.w3.org/2000/svg"><polygon id="empty" points="100,100 400,100 400,400 100,400" /><style>#empty { stroke: black; fill: red; }</style></svg>'))
        return

    def test_geojson_string(self):
        with open("tests/vancouver_island.geojson") as f:
            s = f.read()

        buf = io.StringIO()
        with mapsheet.MapSheet(buf, bbox=(-129, 48, -123, 51)) as sheet:
            sheet.add_geojson(s)

        self.assertEqual(len(sheet.entities), 22)
        return

    def test_svg_circle_static_radius(self):
        s = '''{"type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1.0, 3.0]},
                "properties": {"size": 5.0}}'''
        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.add_geojson(s, radius=3.14)
        buf.seek(0)
        self.assertTrue(xml_equal(buf.read(),
                '<svg height="500" width="500" xmlns="http://www.w3.org/2000/svg"><circle cx="251.389" cy="244.625" r="3.14" /></svg>'))

    def test_svg_circle_dynamic_radius(self):
        s = '''{"type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1.0, 3.0]},
                "properties": {"size": 5.0}}'''
        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.add_geojson(s, prop_radius="size")
        buf.seek(0)
        self.assertTrue(xml_equal(buf.read(),
                '<svg height="500" width="500" xmlns="http://www.w3.org/2000/svg"><circle cx="251.389" cy="244.625" r="5.0" /></svg>'))

    def test_svg_polygon_fill(self):
        s = '''{"type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[1.0, 1.0], [2.0, 1.0], [2.5, 2.0],
                                     [1.5, 2.0], [1.0, 1.0]]]
                    },
                "properties": {"color": "#FF0000"}}'''
        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.add_geojson(s, prop_fill="color")
        buf.seek(0)
        self.assertTrue(xml_equal(buf.read(),
                '<svg height="500" width="500" xmlns="http://www.w3.org/2000/svg"><polygon points="251.389,248.209 252.778,248.209 253.472,246.417 252.083,246.417 251.389,248.209" /></svg>'))

class SVGOutputTests(unittest.TestCase):

    def test_circle(self):
        svg_circle = svg.SVGCircle((1, 3), 5)
        self.assertTrue(xml_equal('<circle cx="1" cy="3" r="5" />', str(svg_circle)))

    def test_polygon(self):
        svg_poly = svg.SVGPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        out = str(svg_poly)
        self.assertTrue(xml_equal('<polygon points="0,0 1,0 1,1 0,1" />', out))

    def test_open_path(self):
        svg_path = svg.SVGPath([(0, 0), (1, 0), (1, 1), (0, 1)], closed=False)
        out = str(svg_path)
        self.assertTrue(xml_equal('<path d="M0,0 L1,0 L0,1 L-1,0" />', out))

    def test_closed_path(self):
        svg_path = svg.SVGPath([(0, 0), (1, 0), (1, 1), (0, 1)], closed=True)
        out = str(svg_path)
        self.assertTrue(xml_equal('<path d="M0,0 L1,0 L0,1 L-1,0 Z" />', out))

if __name__ == "__main__":
    unittest.main()
