import math
import xml.etree.ElementTree as ET
import picogeojson
from .svg import SVGNode, SVGPolygon

class MapSheet(object):
    """ A MapSheet object represents a map image. It is backed by a *dest*,
    which may be a file or an in-memory buffer. It has a *width* and a *height*
    in user coordinates, and a *projection* defining how geographical
    coordinates are mapped to an image.

    Additional keyword arguments
    - *style* sets a CSS stylesheet
    - *bbox* indicates the map extents in geographical (lon, lat) coordinates
    """

    def __init__(self, dest, width=None, height=None, style=None,
            projection="webmercator", bbox=None):

        self.dest = dest
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
            bbox = (-180, -80, 180, 80)

        ll = self.projection(bbox[0], bbox[1])
        ur = self.projection(bbox[2], bbox[3])
        self._bbox = (ll[0], ll[1], ur[0], ur[1])

        def transform(x, y):
            ux = (x-self._bbox[0]) / (self._bbox[2]-self._bbox[0]) * self.width
            uy = (y-self._bbox[1]) / (self._bbox[3]-self._bbox[1]) * self.height
            return ux, uy

        self.transform = transform
        self.width = width
        self.height = height
        self.style = style
        self.entities = []
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None and exc_value is None and traceback is None:

            if hasattr(self.dest, "write"):
                self.dest.write(self.serialize())

            elif isinstance(self.dest, str):
                with open(self.dest, "w") as f:
                    f.write(self.serialize())

        return False # re-raise exceptions

    def add(self, *args, **kwargs):
        """ Add one or more entities to the MapSheet. Inputs may be
        - subclasses of SVGNode
        - picogeojson geometries
        """
        for arg in args:
            if isinstance(arg, SVGNode):
                self.entities.append(arg)
            else:
                self.entities.extend(self.from_geojson(arg, **kwargs))
        return

    def from_geojson(self, geojson, circle_radius=1.0, **kw):

        def flip(x, y):
            return x, self.height-y

        results = []

        if isinstance(geojson, picogeojson.types.Point):
            vert = flip(*self.transform(*self.projection(*geojson.coordinates)))
            results.append(SVGCircle(vert, circle_radius, **kw))

        elif isinstance(geojson, picogeojson.types.LineString):
            verts = [flip(*self.transform(*self.projection(*xy)))
                        for xy in geojson.coordinates]
            results.append(SVGPath(verts, **kw))

        elif isinstance(geojson, picogeojson.types.Polygon):
            for ring in geojson.coordinates:
                verts = [flip(*self.transform(*self.projection(*xy)))
                        for xy in ring]
                results.append(SVGPolygon(verts, **kw))

        else:
            raise NotImplementedError()
        return results

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

def project_webmercator(lon, lat):
    x = 128 / math.pi * (lon*math.pi/180.0 + math.pi)
    y = 128 / math.pi * (math.pi - math.log(math.tan(math.pi * (0.25 + lat/360))))
    return x, y
