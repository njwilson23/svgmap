""" Implements an abstraction over SVG elements """

import xml.etree.ElementTree as ET


class SVGNode(object):

    def __init__(self, name, id_name=None, class_name=None, precision=2, **kw):
        self.name = name
        self.precision = precision
        self.attrs = {}
        for key, value in kw.items():
            self.attrs[key.replace("_", "-")] = str(value)
        if id_name is not None:
            self.attrs["id"] = id_name
        if class_name is not None:
            self.attrs["class"] = class_name

    def __str__(self):
        return ET.tostring(self.svg(), encoding="unicode")

    def svg(self):
        return ET.Element(self.name, attrib=self.attrs)


class SVGRoot(SVGNode):

    def __init__(self, width, height):
        super(SVGRoot, self).__init__("svg")
        self.attrs["width"] = str(width)
        self.attrs["height"] = str(height)
        self.attrs["xmlns"] = "http://www.w3.org/2000/svg"


class SVGCircle(SVGNode):

    def __init__(self, vertex, radius, **kw):
        super(SVGCircle, self).__init__("circle", **kw)
        self.attrs["cx"] = str(round(vertex[0], self.precision))
        self.attrs["cy"] = str(round(vertex[1], self.precision))
        self.attrs["r"] = str(round(radius, self.precision))


class SVGPath(SVGNode):

    def __init__(self, vertices, closed=False, **kw):
        self.vertices = vertices
        self.closed = closed
        super(SVGPath, self).__init__("path", **kw)

    def svg(self):
        d = []
        for linestring in self.vertices:
            d.append("M{x},{y}".format(x=round(linestring[0][0], self.precision),
                                       y=round(linestring[0][1], self.precision)))
            d.extend(["L{x},{y}".format(x=round(x, self.precision),
                                        y=round(y, self.precision))
                                        for (x, y) in linestring[1:]])
            if self.closed:
                d.append("Z")
        self.attrs["d"] = " ".join(d)
        return ET.Element("path", attrib=self.attrs)


class SVGPolygon(SVGNode):

    def __init__(self, vertices, **kw):
        super(SVGPolygon, self).__init__("polygon", **kw)
        point_string = " ".join(["{x},{y}".format(x=round(x, self.precision),
                                                  y=round(y, self.precision))
                                                  for (x, y) in vertices])
        self.attrs["points"] = point_string

