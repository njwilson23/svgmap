import math
import xml.etree.ElementTree as ET
import picogeojson
from .svg import SVGNode, SVGPolygon

class MapSheet(object):
    """ A MapSheet object represents a map image """

    def __init__(self, width=None, height=None, style=None, projection="webmercator", bbox=None):
        self.projection = projection

        if width is None:
            width = 500
        if height is None:
            height = 500
        if style is None:
            style = {}

        if projection == "webmercator":
            self.projection = project_webmercator
        else:
            raise NotImplementedError()

        if bbox is None:
            ll = self.projection(-180, -80)
            ur = self.projection(180, 80)
            self.bbox = (ll[0], ll[1], ur[0], ur[1])
        else:
            self.bbox = bbox

        def transform(x, y):
            ux = (x-self.bbox[0]) / (self.bbox[2]-self.bbox[0]) * self.width
            uy = (y-self.bbox[1]) / (self.bbox[3]-self.bbox[1]) * self.height
            return ux, uy

        self.transform = transform
        self.width = width
        self.height = height
        self.style = style
        self.entities = []
        return

    def from_geojson(self, geojson, **kw):

        def flip(x, y):
            return x, self.height-y

        results = []
        if isinstance(geojson, picogeojson.types.Polygon):
            for ring in geojson.coordinates:
                verts = [flip(*self.transform(*self.projection(*xy))) for xy in ring]
                results.append(SVGPolygon(verts, **kw))
        else:
            raise NotImplementedError()
        return results


    def add(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, SVGNode):
                self.entities.append(arg)
            else:
                self.entities.extend(self.from_geojson(arg, **kwargs))
        return

    def serialize(self):
        root = ET.Element("svg", attrib={
                                "width": str(self.width),
                                "height": str(self.height),
                                "xmlns": "http://www.w3.org/2000/svg"
                          })

        for entity in self.entities:
            root.append(entity.svg())

        if len(self.style) != 0:
            style = ET.Element("style")
            style.text = self.style
            root.append(style)

        return ET.tostring(root, encoding="unicode")

class MapFile(object):

    def __init__(self, filename, **kw):
        self.filename = filename
        self.mapsheet = MapSheet(**kw)
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with open(self.filename, "w") as f:
            f.write(self.mapsheet.serialize())

    def add(self, *args):
        self.mapsheet.add(*args)

def project_webmercator(lon, lat):
    x = 128 / math.pi * (lon*math.pi/180.0 + math.pi)
    y = 128 / math.pi * (math.pi - math.log(math.tan(math.pi * (0.25 + lat/360))))
    return x, y
