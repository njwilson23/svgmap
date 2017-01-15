# svgmap

Compose GeoJSON/TopoJSON vector features into SVG maps.

## Demo

```python
import picogeojson
import svgmap

feature_collection = picogeojson.fromfile("island.geojson")

with svgmap.mapsheet.MapFile("demo.svg", bbox=(36.25, 89, 41.25, 85.5)) as mapfile:

    mapfile.mapsheet.style = """
    polygon { fill: lightsteelblue; transition-duration: 0.5s; }
    polygon:hover { fill: cadetblue; transition-duration: 0.3s; }
    """

    for feature in feature_collection.features:
        mapfile.add(feature.geometry)
```
produces

![Vancouver Island](https://cdn.rawgit.com/njwilson23/svgmap/master/doc/demo.svg)

