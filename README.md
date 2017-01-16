# svgmap

Compose GeoJSON/TopoJSON vector features into SVG maps.

## Demo

```python
import picogeojson
import svgmap

feature_collection = picogeojson.fromfile("island.geojson")

with svgmap.MapSheet("demo.svg", bbox=(-129, 48, -123, 51)) as mapsheet:

    mapsheet.style = """
    polygon { fill: lightsteelblue; transition-duration: 0.5s; }
    polygon:hover { fill: cadetblue; transition-duration: 0.3s; }
    """

    for feature in features.features:
        mapsheet.add(feature.geometry)
```
produces

![Vancouver Island](https://cdn.rawgit.com/njwilson23/svgmap/master/doc/demo.svg)

