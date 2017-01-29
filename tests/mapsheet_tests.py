import unittest
import io
import xml.etree.ElementTree as ET
from worldly import svg, mapsheet
from util import xml_equal

class MapSheetTests(unittest.TestCase):

    def test_simple_map(self):

        poly = svg.SVGPolygon([(100, 100), (400, 100), (400, 400), (100, 400)],
                              id_name="empty")

        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.style = "#empty { stroke: black; fill: red; }"
            sheet.add_svg(poly)

        buf.seek(0)
        s = buf.read()
        self.assertTrue('<svg height="500" width="500" xmlns="http://www.w3.org/2000/svg">'
                        in s)
        self.assertTrue("<style>#empty { stroke: black; fill: red; }</style>"
                        in s)
        self.assertTrue('<polygon id="empty" points="100,100 400,100 400,400 100,400" />'
                        in s)

    def test_geojson_string(self):
        with open("tests/vancouver_island.geojson") as f:
            s = f.read()

        buf = io.StringIO()
        with mapsheet.MapSheet(buf, bbox=(-129, 48, -123, 51)) as sheet:
            sheet.add_geojson(s)

        self.assertEqual(len(sheet.entities), 22)

    def test_svg_point_static_radius(self):
        s = '''{"type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1.0, 3.0]},
                "properties": {"size": 5.0}}'''
        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.add_geojson(s, static_params={"stroke-width":3.14})
        buf.seek(0)
        self.assertTrue('stroke-width="3.14"' in buf.read())

    def test_svg_point_dynamic_radius(self):
        s = '''{"type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1.0, 3.0]},
                "properties": {"size": 5.0}}'''
        buf = io.StringIO()
        with mapsheet.MapSheet(buf) as sheet:
            sheet.add_geojson(s, dynamic_params={"stroke-width":"size"})
        buf.seek(0)
        self.assertTrue('stroke-width="5.0"' in buf.read())

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
            sheet.add_geojson(s, dynamic_params=dict(fill="color"))
        buf.seek(0)
        self.assertTrue('fill="#FF0000"' in buf.read())

if __name__ == "__main__":
    unittest.main()
