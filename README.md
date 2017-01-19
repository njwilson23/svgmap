# Worldy

Compose GeoJSON/TopoJSON vector features into SVG maps.

## Demo

```python
import requests
import worldly

with worldly.MapSheet("demo.svg", bbox=(-134, 51, -130, 55)) as mapsheet:

    mapsheet.style = """
    polygon { fill: #222222 }
    .earthquake { fill: firebrick; }
    """

    mapsheet.add_geojson_file("tests/haidagwai.geojson")

    r = requests.get("http://earthquake.usgs.gov/fdsnws/event/1/query?",
                     {"format":      "geojson",
                      "starttime":   "2012-01-16",
                      "endtime":     "2017-01-15",
                      "latitude":    53,
                      "longitude":   -132,
                      "maxradiuskm": 200})

    if r.status_code == 200:
        mapsheet.add_geojson(r.text,
                             prop_radius="magnitude",
                             rscale=lambda a: 0.1*a*a,
                             class_name="earthquake")
```
produces

![Vancouver Island](https://cdn.rawgit.com/njwilson23/worldly/master/doc/demo.svg)

