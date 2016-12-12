
class SVGNode(object):

    pass

class SVGPath(SVGNode):

    def __init__(self, vertices, projection=None, closed=False):
        self.vertices = vertices
        self.projection = projection
        self.closed = closed

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
        return '<path d="{d}"/>'.format(d=d)

class SVGPolygon(SVGNode):

    def __init__(self, vertices, projection=None):
        self.vertices = vertices
        self.projection = projection

    def svg(self):
        ptstr = " ".join(["{0},{1}".format(x, y) for (x, y) in self.vertices])
        return '<polygon points="{0}"/>'.format(ptstr)

