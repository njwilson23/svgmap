import xml.etree.ElementTree as ET

class SVGNode(object):

    def __init__(self, id_name=None, class_name=None, **kw):
        self.attrs = {}
        for key, value in kw.items():
            self.attrs[key.replace("_", "-")] = str(value)
        if id_name is not None:
            self.attrs["id"] = id_name
        if class_name is not None:
            self.attrs["class"] = class_name
        return

    def __str__(self):
        return ET.tostring(self.svg(), encoding="unicode")

class SVGCircle(SVGNode):

    def __init__(self, vertex, radius, **kw):
        self.vertex = vertex
        self.radius = radius
        super(SVGCircle, self).__init__(**kw)
        return

    def svg(self):
        self.attrs["cx"] = str(round(self.vertex[0], 3))
        self.attrs["cy"] = str(round(self.vertex[1], 3))
        self.attrs["r"] = str(round(self.radius, 3))
        return ET.Element("circle", attrib=self.attrs)

class SVGPath(SVGNode):

    def __init__(self, vertices, closed=False, **kw):
        self.vertices = vertices
        self.closed = closed
        super(SVGPath, self).__init__(**kw)
        return

    def svg(self):
        d = []
        for linestring in self.vertices:
            sx = linestring[0][0]
            sy = linestring[0][1]
            Dx = [b[0]-a[0] for a, b in zip(linestring[:-1], linestring[1:])]
            Dy = [b[1]-a[1] for a, b in zip(linestring[:-1], linestring[1:])]
            d.append("M{sx},{sy}".format(sx=round(sx, 6), sy=round(sy, 6)))
            d.extend(["l{dx},{dy}".format(dx=round(dx, 6), dy=round(dy, 6))
                      for (dx, dy) in zip(Dx, Dy)])
            if self.closed:
                d.append("Z")

        self.attrs["d"] = " ".join(d)
        return ET.Element("path", attrib=self.attrs)

class SVGPolygon(SVGNode):

    def __init__(self, vertices, **kw):
        self.vertices = vertices
        super(SVGPolygon, self).__init__(**kw)
        return

    def svg(self):
        point_string = " ".join(["{0},{1}".format(round(x, 3), round(y, 3)) for (x, y) in self.vertices])
        self.attrs["points"] = point_string
        return ET.Element("polygon", attrib=self.attrs)



