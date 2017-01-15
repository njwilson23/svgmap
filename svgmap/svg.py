
import xml.etree.ElementTree as ET

class SVGNode(object):

    def __str__(self):
        return ET.tostring(self.svg(), encoding="unicode")

class SVGPath(SVGNode):

    def __init__(self, vertices, closed=False, id_name=None, class_name=None):
        self.vertices = vertices
        self.closed = closed
        self.id_name = id_name
        self.class_name = class_name

    def svg(self):
        ptstr = " ".join(["{0},{1}".format(x, y) for (x, y) in self.vertices])
        sx = self.vertices[0][0]
        sy = self.vertices[0][1]
        Dx = [b[0]-a[0] for a, b in zip(self.vertices[:-1], self.vertices[1:])]
        Dy = [b[1]-a[1] for a, b in zip(self.vertices[:-1], self.vertices[1:])]
        _d = ["M{sx},{sy}".format(sx=sx, sy=sy)] + \
             ["L{dx},{dy}".format(dx=dx, dy=dy) for (dx, dy) in zip(Dx, Dy)]
        if self.closed:
            _d.append("Z")
        d = " ".join(_d)

        attrs = {"d": d}
        if self.id_name is not None:
            attrs["id"] = self.id_name
        if self.class_name is not None:
            attrs["class"] = self.class_name
        return ET.Element("path", attrib=attrs)

class SVGPolygon(SVGNode):

    def __init__(self, vertices, id_name=None, class_name=None):
        self.vertices = vertices
        self.id_name = id_name
        self.class_name = class_name

    def svg(self):
        point_string = " ".join(["{0},{1}".format(x, y) for (x, y) in self.vertices])

        attrs = {"points": point_string}
        if self.id_name is not None:
            attrs["id"] = self.id_name
        if self.class_name is not None:
            attrs["class"] = self.class_name
        return ET.Element("polygon", attrib=attrs)

