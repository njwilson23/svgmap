import math
import xml.etree.ElementTree as ET
import picogeojson
from .svg import SVGNode, SVGCircle, SVGPolygon, SVGPath

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
        return [self._add_geojson_tuple(picogeojson.fromstring(s), **kw)
                for s in strings]

    def add_svg(self, *svgnodes):
        """ Add raw SVGNodes """
        for node in svgnodes:
            if isinstance(node, SVGNode):
                self.entities.append(node)
            else:
                raise ValueError("{} not an instance of SVGNode".format(node))

    def _add_geojson_tuple(self, *inputs, **kw):
        """ Convert picogeojson namedtuples to SVGNodes and add to self.entities

        Keyword arguments
        -----------------
        class_name : str
        id_name : str
        """
        static_params = kw.get("static_params", {})
        dynamic_params = kw.get("dynamic_params", {})
        scales = kw.get("scales", {})
        class_name = kw.get("class_name", None)
        id_name = kw.get("id_name", None)

        pending = [a for a in inputs]
        results = []
        while len(pending) != 0:

            geojson = pending[0]
            pending = pending[1:]

            if type(geojson).__name__ == "FeatureCollection":
                pending.extend(geojson.features)
            elif type(geojson).__name__ == "Feature":
                intermediate = self._geometry_to_svg(geojson.geometry, class_name=class_name, id_name=id_name)
                _set_attrs(intermediate, static_params, scales)
                _set_attrs_from_properties(intermediate, dynamic_params, scales,
                                           geojson.properties)
                results.extend(intermediate)
            else:
                intermediate = self._geometry_to_svg(geojson, class_name=class_name, id_name=id_name)
                _set_attrs(intermediate, static_params, scales)
                results.extend(intermediate)

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

    def _geometry_to_svg(self, geojson, class_name=None, id_name=None):

        def flip_y(x, y):
            return x, self.height-y

        results = []
        pending = [geojson]
        while len(pending) != 0:
            geojson = pending[0]
            pending = pending[1:]

            if type(geojson).__name__ == "Point":
                vert = flip_y(*self.transform(*self.projection(*geojson.coordinates)))
                results.append(SVGPath([[vert]], closed=True, stroke_linecap="round", class_name=class_name, id_name=id_name))

            elif type(geojson).__name__ == "LineString":
                verts = [flip_y(*self.transform(*self.projection(*xy)))
                            for xy in geojson.coordinates]
                results.append(SVGPath([verts], class_name=class_name, id_name=id_name))

            elif type(geojson).__name__ == "Polygon":
                ring_list = []
                for ring in geojson.coordinates:
                    verts = [flip_y(*self.transform(*self.projection(*xy)))
                            for xy in ring]
                    ring_list.append(verts)
                results.append(SVGPath(ring_list, closed=True, class_name=class_name, id_name=id_name))

            elif type(geojson).__name__ == "MultiPoint":
                verts = []
                for xy in geojson.coordinates:
                    v = flip_y(*self.transform(*self.projection(*xy)))
                    verts.append(v)
                verts_listed = [[v] for v in verts]
                results.append(SVGPath(verts_listed, closed=True, stroke_linecap="round", class_name=class_name, id_name=id_name))

            elif type(geojson).__name__ == "MultiLineString":
                verts = []
                for ls in geojson.coordinates:
                    v = [flip_y(*self.transform(*self.projection(*xy)))
                         for xy in geojson.vertices]
                    verts.append(v)
                results.append(SVGPath(verts, class_name=class_name, id_name=id_name))

            elif type(geojson).__name__ == "MultiPolygon":
                poly_vert_list
                for poly in geojson.coordinates:
                    ring_vert_list = []
                    for ring in poly:
                        verts = [flip_y(*self.transform(*self.projection(*xy)))
                                for xy in ring]
                        ring_vert_list.append(verts)
                    poly_vert_list.extend(ring_vert_list)
                results.append(SVGPolygon(poly_vert_list, closed=True))

            elif type(geojson).__name__ == "GeometryCollection":
                for g in geojson.geometries:
                    pending.append(g)

            else:
                raise NotImplementedError("'{}' not handled".format(type(geojson)))

        return results

def _set_attrs(geoms, params, scales):
    for k, v in params.items():
        func = scales.get(k, lambda a: a)
        for geom in geoms:
            geom.attrs[k] = str(func(v))
    return

def _set_attrs_from_properties(geoms, params, scales, properties):
    computed_params = {}
    for k, v in params.items():
        func = scales.get(k, lambda a: a)
        if v in properties:
            computed_params[k] = str(func(properties[v]))
    for geom in geoms:
        geom.attrs.update(computed_params)
    return

def project_webmercator(lon, lat, z=None):
    x = 128 / math.pi * (lon*math.pi/180.0 + math.pi)
    y = 128 / math.pi * (math.pi - math.log(math.tan(math.pi * (0.25 + lat/360))))
    return x, y
