import requests
import worldly

with worldly.MapSheet("demo.svg", bbox=(-134, 51, -130, 55)) as mapsheet:

    mapsheet.style = """
    .land { fill: #333333; }
    .earthquake { stroke: chocolate;
                  opacity: 0.9; }
    """

    mapsheet.add_geojson_file("tests/haidagwai.geojson", class_name="land")

    r = requests.get("http://earthquake.usgs.gov/fdsnws/event/1/query?",
                     {"format":      "geojson",
                      "starttime":   "2012-01-26",
                      "endtime":     "2017-01-25",
                      "latitude":    53.22,
                      "longitude":   -132.24,
                      "maxradiuskm": 250})

    if r.status_code == 200:
        mapsheet.add_geojson(r.text,
                             dynamic_params={"stroke-width": "mag"},
                             scales={"stroke-width": lambda a: 0.3*a*a},
                             class_name="earthquake")

