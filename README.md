# Static SVG maps

The *svgmaps* package makes it simple to create geographically-correct SVG maps
from Python.

Example:

```python
import svgmaps
from svgmaps import Map, Stylesheet, graticule, scalebar

continents = svgmaps.read_geojson("world_land.json")

with Map("world_map.svg", projection="Mercator") as mapsheet:
    mapsheet.stylesheet = Stylesheet("style.css")
    mapsheet.add(continents)
    mapsheet.add(graticule)
    mapsheet.add(scalebar, "lower right")
```

Generates the following image:

[...]


Maps can be bound to data to create chloropleth maps:

```python
import svgmaps
from svgmaps import Map, graticule, scalebar

states = svgmaps.read_geojson("world_land.json")

with Map("world_map.svg", projection="USA-albers") as mapsheet:
    mapsheet.stylesheet = Stylesheet("style.css")
    mapsheet.add(states, fill_color="pop_dens_2010", edge_color="none")
```


The alpha version of *svgmaps* depends on the *Karta* geospatial package, but
may become completely independent in the future.

