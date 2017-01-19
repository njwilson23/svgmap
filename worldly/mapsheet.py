import math
import xml.etree.ElementTree as ET
import picogeo
from .svg import SVGNode, SVGCircle, SVGPolygon

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

    def add_geojson_file(self, filename, **kw):
        """ Add contents of a GeoJSON file """
        with open(filename) as f:
            ret = self.add_geojson(f.read(), **kw)
        return ret

    def add_geojson(self, *strings, **kw):
        """ Add GeoJSON strings """
        return [self._add_picogeojson_tuple(picogeo.fromstring(s), **kw)
                for s in strings]

    def add_svg(self, *svgnodes):
        """ Add raw SVGNodes """
        for node in svgnodes:
            if isinstance(node, SVGNode):
                self.entities.append(node)
            else:
                raise ValueError("{} not an instance of SVGNode".format(node))

    def _add_picogeojson_tuple(self, *inputs, **kw):
        """ Convert picogeo namedtuples to SVGNodes and add to self.entities

        Keyword arguments
        -----------------
        class_name : str
        id_name : str
        radius : float
            applied to the <circle> radius used to represent Point, MultiPoint
        """
        cls_name = kw.get("class_name", None)
        id_name = kw.get("id_name", None)
        cls_id = {}
        if cls_name is not None:
            cls_id["class_name"] = cls_name
        if id_name is not None:
            cls_id["id_name"] = id_name

        svg_attrs = {}
        for name in ("fill", "stroke", "stroke_width"):
            if name in kw:
                svg_attrs[name.replace("_", "-")] = kw[name]


        radius_scale = kw.get("rscale", lambda a: a)

        def flip_y(x, y):
            return x, self.height-y

        pending = [(a, {}) for a in inputs]
        results = []

        while len(pending) != 0:

            geojson, params = pending[0]
            pending = pending[1:]

            if isinstance(geojson, picogeo.types.Point):
                r = radius_scale(params.get(kw.get("radius", None), 4.0))
                vert = flip_y(*self.transform(*self.projection(*geojson.coordinates)))
                results.append(SVGCircle(vert, r, **cls_id, **svg_attrs))

            elif isinstance(geojson, picogeo.types.LineString):
                verts = [flip_y(*self.transform(*self.projection(*xy)))
                            for xy in geojson.coordinates]
                results.append(SVGPath(verts, **cls_id, **svg_attrs))

            elif isinstance(geojson, picogeo.types.Polygon):
                for ring in geojson.coordinates:
                    verts = [flip_y(*self.transform(*self.projection(*xy)))
                            for xy in ring]
                    results.append(SVGPolygon(verts, **cls_id, **svg_attrs))

            elif isinstance(geojson, picogeo.types.MultiPoint):
                r = radius_scale(params.get(kw.get("radius", None), 4.0))
                for vert in geojson.coordinates:
                    vert_ = flip_y(*self.transform(*self.projection(*geojson.coordinates)))
                    results.append(SVGCircle(vert_, r, **cls_id, **svg_attrs))

            elif isinstance(geojson, picogeo.types.MultiLineString):
                for ls in geojson.coordinates:
                    verts = [flip_y(*self.transform(*self.projection(*xy)))
                             for xy in verts]
                    results.append(SVGPath(verts, **cls_id, **svg_attrs))

            elif isinstance(geojson, picogeo.types.MultiPolygon):
                for poly in geojson.coordinates:
                    for ring in poly:
                        verts = [flip_y(*self.transform(*self.projection(*xy)))
                                for xy in ring]
                        results.append(SVGPolygon(verts, **cls_id, **svg_attrs))

            elif isinstance(geojson, picogeo.types.GeometryCollection):
                for g in geojson.geometries:
                    pending.append((g, {}))

            elif isinstance(geojson, picogeo.types.Feature):
                pending.append((geojson.geometry, geojson.properties))

            elif isinstance(geojson, picogeo.types.FeatureCollection):
                for g in geojson.features:
                    pending.append((g, {}))

            else:
                raise NotImplementedError()
        self.entities.extend(results)
        return results

    def serialize(self):
        """ Return an encoded SVG string """
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

def project_webmercator(lon, lat, z=None):
    x = 128 / math.pi * (lon*math.pi/180.0 + math.pi)
    y = 128 / math.pi * (math.pi - math.log(math.tan(math.pi * (0.25 + lat/360))))
    return x, y
