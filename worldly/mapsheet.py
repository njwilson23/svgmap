from math import sqrt
import xml.etree.ElementTree as ET
import picogeojson
from .svg import SVGNode, SVGRoot, SVGPath
from .projection import WebMercator


class MapSheet(object):
    """ A MapSheet object represents a map image. It is backed by a *dest*,
    which may be a file or an in-memory buffer. It has a *width* and a *height*
    in user coordinates, and a *projection* defining how geographical
    coordinates are mapped to an image.

    The scale and spatial extent are determined from a combination of *bbox*,
    *center*, *scale*, and the map pane dimensions. In order of priority,

    1. If *bbox* is provided, then the scale is computed.
    2. If *scale* and *center* are provided, *bbox* is computed.
    3. If only *scale* is provided, *bbox* is computed assuming the map center
       is the centroid of the map entities.
    4. If none are provided, *bbox* is taken from the map entities and scale is
       computed.

    style : str
        CSS string

    projection : callable
        transforms coordinate pairs from geographical space to map space

    bbox : tuple of 4 floats

    scale : float
        indicates the number of pixels per projected unit
        e.g. 1/1000 in a projection defined in meters means that each pixels
        represents 1 km.

    center : tuple of 2 floats
        the map center, in geographical coordinates. Ignored if *bbox* is not
        None. If *center* and *bbox* are None, the centroid of the map entities
        is used.
    """
    def __init__(self, dest, width=500, height=500, style=None,
                 projection=WebMercator, bbox=None, scale=None, center=None):
        self.dest = dest
        self.width = width
        self.height = height
        if style is None:
            style = {}
        self.style = style
        self.projection = projection
        self.bbox = bbox
        self.scale = scale
        self.center = center

        self.entities = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None and exc_value is None and traceback is None:
            if hasattr(self.dest, "write"):
                self.dest.write(self.serialize())
            elif isinstance(self.dest, str):
                with open(self.dest, "w") as f:
                    f.write(self.serialize())
        return False  # re-raise exceptions

    def add_geojson_file(self, filename, **kw):
        """ Add contents of a GeoJSON file """
        with open(filename) as f:
            self.add_geojson(f.read(), **kw)

    def add_geojson(self, *strings, **kw):
        """ Add GeoJSON strings """
        for string in strings:
            self.entities.append((picogeojson.fromstring(string), kw))

    def add_svg(self, *svgnodes):
        """ Add raw SVGNodes """
        for node in svgnodes:
            if isinstance(node, SVGNode):
                self.entities.append((node, {}))
            else:
                raise ValueError("{} not an instance of SVGNode".format(node))

    def serialize(self):
        """ Return an encoded SVG string """

        precision = 1

        if self.scale is None:      # compute scale from bbox
            bbox = (-180, -80, 180, 80) if self.bbox is None else self.bbox
            ll = self.projection(bbox[0], bbox[1])
            ur = self.projection(bbox[2], bbox[3])
            bbox_p = (ll[0], ll[1], ur[0], ur[1])
            d = sqrt((bbox_p[2] - bbox_p[1])**2 + (bbox_p[3] - bbox_p[1])**2)
            L = sqrt(self.width**2 + self.height**2)
            scale = L/d

        else:                       # compute bbox from scale
            scale = self.scale

            _bboxes = [projected_bbox(entity, self.projection)
                       for entity, _ in self.entities
                       if not isinstance(entity, SVGNode)]
            _bbox_p = (min(bb[0] for bb in _bboxes),
                       min(bb[1] for bb in _bboxes),
                       max(bb[2] for bb in _bboxes),
                       max(bb[3] for bb in _bboxes))
            cen = (0.5*(_bbox_p[0] + _bbox_p[2]), 0.5*(_bbox_p[1] + _bbox_p[3]))
            dx = 0.5 * self.height / scale
            dy = 0.5 * self.width / scale
            bbox_p = (cen[0] - dx, cen[1] + dy, cen[0] + dx, cen[1] - dy)

        transform = ("translate({dx1},{dy1}) "
                     "scale({sx},{sy}) "
                     "translate({dx0},{dy0})".format(
                     sx=self.width / (bbox_p[2]*scale - bbox_p[0]*scale),
                     sy=-self.height / (bbox_p[3]*scale - bbox_p[1]*scale),
                     dx1=0.5*self.width,
                     dy1=0.5*self.height,
                     dx0=-0.5*(bbox_p[0]*scale + bbox_p[2]*scale),
                     dy0=-0.5*(bbox_p[1]*scale + bbox_p[3]*scale)))

        def scalefunc(xy):
            return [a*scale for a in xy[:2]]

        svgs = []
        for entity, params in self.entities:
            if isinstance(entity, SVGNode):
                svgs.append(entity)
            else:
                g = _convert_geojson_tuple(entity, scalefunc, self.projection,
                                           precision, **params)
                svgs.extend(g)

        root = SVGRoot(self.width, self.height).svg()
        g = SVGNode("g", transform=transform).svg()

        for item in svgs:
            g.append(item.svg())

        if len(self.style) != 0:
            style = ET.Element("style")
            style.text = self.style
            root.append(style)

        root.append(g)
        return ET.tostring(root, encoding="unicode")

def _convert_geojson_tuple(geojson, scale, projection, precision, **kw):
    """ Converts a picogeojson namedtuple to a list of SVGNode instances

    arguments
    ---------
    geojson : picogeojson namedtuple
        geometry, feature, or featurecollection to convert
    scale : function
        rescales projected coordinates to map space
    projection : function
        projects geographical coordinates to cartesian coordinates
    precision : float
        number of decimal places to retain in svg coordinates

    keyword arguments
    -----------------
    class_name : str
        used as class attribute
    id_name : str
        used as id attribute
    """
    static_params = kw.get("static_params", {})
    dynamic_params = kw.get("dynamic_params", {})
    scales = kw.get("scales", {})
    class_name = kw.get("class_name", None)
    id_name = kw.get("id_name", None)

    pending = [geojson]
    results = []
    while len(pending) != 0:

        geojson = pending[0]
        pending = pending[1:]

        if type(geojson).__name__ == "FeatureCollection":
            pending.extend(geojson.features)
        elif type(geojson).__name__ == "Feature":
            intermediate = _geometry_to_svg(geojson.geometry,
                                            scale, projection,
                                            precision=precision,
                                            class_name=class_name,
                                            id_name=id_name)
            _set_attrs(intermediate, static_params, scales)
            _set_attrs_from_properties(intermediate, dynamic_params, scales,
                                       geojson.properties)
            results.extend(intermediate)
        else:
            intermediate = _geometry_to_svg(geojson,
                                            scale, projection,
                                            precision=precision,
                                            class_name=class_name,
                                            id_name=id_name)
            _set_attrs(intermediate, static_params, scales)
            results.extend(intermediate)

    return results

def _geometry_to_svg(geojson, scale, projection, precision=6,
                     class_name=None, id_name=None):
    """ Converts a picogeojson Geometry to a list of SVGNode instances.
    See _convert_geojson_tuple for parameters
    """
    results = []
    pending = [geojson]
    while len(pending) != 0:
        geojson = pending[0]
        pending = pending[1:]

        if type(geojson).__name__ == "Point":
            vert = scale(projection(*geojson.coordinates[:2]))
            results.append(SVGPath([[vert]],
                                   closed=True,
                                   stroke_linecap="round",
                                   precision=precision,
                                   class_name=class_name,
                                   id_name=id_name))

        elif type(geojson).__name__ == "LineString":
            verts = [scale(projection(*xy[:2])) for xy in geojson.coordinates]
            results.append(SVGPath([verts], class_name=class_name,
                                            id_name=id_name))

        elif type(geojson).__name__ == "Polygon":
            ring_list = []
            for ring in geojson.coordinates:
                verts = [scale(projection(*xy[:2])) for xy in ring]
                ring_list.append(verts)
            results.append(SVGPath(ring_list,
                                   closed=True,
                                   precision=precision,
                                   class_name=class_name,
                                   id_name=id_name))

        elif type(geojson).__name__ == "MultiPoint":
            verts = []
            for xy in geojson.coordinates:
                v = scale(projection(*xy[:2]))
                verts.append(v)
            verts_listed = [[v] for v in verts]
            results.append(SVGPath(verts_listed,
                                   closed=True,
                                   stroke_linecap="round",
                                   precision=precision,
                                   class_name=class_name,
                                   id_name=id_name))

        elif type(geojson).__name__ == "MultiLineString":
            linestrings = []
            for ls in geojson.coordinates:
                v = [scale(projection(*xy[:2])) for xy in ls]
                linestrings.append(v)
            results.append(SVGPath(linestrings,
                                   precision=precision,
                                   class_name=class_name,
                                   id_name=id_name))

        elif type(geojson).__name__ == "MultiPolygon":
            poly_list = []
            for poly in geojson.coordinates:
                ring_list = []
                for ring in poly:
                    verts = [scale(projection(*xy[:2])) for xy in ring]
                    ring_list.append(verts)
                poly_list.extend(ring_list)
            results.append(SVGPath(poly_list,
                                   closed=True,
                                   precision=precision,
                                   class_name=class_name,
                                   id_name=id_name))

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

def project_nested(coordinates, projection):
    if not hasattr(coordinates[0], "__iter__"):
        return projection(*coordinates[:2])
    else:
        return [project_nested(crds, projection) for crds in coordinates]

def apply_index_nested(coordinates, func, idx):
    """ Applies a function f([a...]) -> b to a list built from the *idx*-th
    component of every item in an arbitrarily-nested list.
    """
    if not hasattr(coordinates[0][0], "__iter__"):
        return func([xy[idx] for xy in coordinates])
    else:
        return func(apply_index_nested(crds, func, idx) for crds in coordinates)

def projected_bbox(geojson, projection):
    if type(geojson).__name__ == "Point":
        pcrds = project_nested(geojson.coordinates, projection)
        bbox = (pcrds[0], pcrds[1], pcrds[0], pcrds[1])
    elif hasattr(geojson, "coordinates"):
        pcrds = project_nested(geojson.coordinates, projection)
        xmin = apply_index_nested(pcrds, min, 0)
        ymin = apply_index_nested(pcrds, min, 1)
        xmax = apply_index_nested(pcrds, max, 0)
        ymax = apply_index_nested(pcrds, max, 1)
        bbox = (xmin, ymin, xmax, ymax)
    elif hasattr(geojson, "geometry"):
        bbox = projected_bbox(geojson.geometry, projection)
    elif hasattr(geojson, "geometries"):
        bbs = [projected_bbox(g, projection) for g in geojson.geometries]
        bbox = (min(bb[0] for bb in bbs), min(bb[1] for bb in bbs),
                max(bb[2] for bb in bbs), max(bb[3] for bb in bbs))
    elif hasattr(geojson, "features"):
        bbs = [projected_bbox(feat.geometry, projection) for feat in geojson.features]
        bbox = (min(bb[0] for bb in bbs), min(bb[1] for bb in bbs),
                max(bb[2] for bb in bbs), max(bb[3] for bb in bbs))
    else:
        raise TypeError("unhandled geometry: '{}'".format(type(geojson)))
    return bbox

