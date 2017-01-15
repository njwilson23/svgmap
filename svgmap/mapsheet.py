
import xml.etree.ElementTree as ET

class MapSheet(object):
    """ A MapSheet object represents a map image """

    def __init__(self, width=None, height=None, style=None, projection="merc"):
        self.projection = projection

        if width is None:
            width = 500
        if height is None:
            height = 500
        if style is None:
            style = {}

        self.width = width
        self.height = height
        self.style = style
        self.entities = []
        return

    def add(self, *args):
        self.entities.extend(args)

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
