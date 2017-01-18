# svgmap

Compose GeoJSON/TopoJSON vector features into SVG maps.

## Demo

```python
import requests
import svgmap

with svgmap.MapSheet("demo.svg", bbox=(-129, 47.5, -122, 51)) as mapsheet:

    mapsheet.style = """
    polygon { fill: lightsteelblue; transition-duration: 0.5s; }
    polygon:hover { fill: cadetblue; transition-duration: 0.3s; }
    .earthquake { fill: firebrick; }
    """

    mapsheet.add_geojson_file("vancouver_island.geojson")

    r = requests.get("http://earthquake.usgs.gov/fdsnws/event/1/query?",
                     {"format":      "geojson",
                      "starttime":   "2016-01-01",
                      "endtime":     "2017-01-15",
                      "latitude":    49,
                      "longitude":   -124,
                      "maxradiuskm": 300})

    if r.status_code == 200:
        mapsheet.add_geojson(r.text, radius=3.0, class_name="earthquake")
```
produces

![Vancouver Island](https://cdn.rawgit.com/njwilson23/svgmap/master/doc/demo.svg)

