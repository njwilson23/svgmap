# SVG display maps

The *Worldly* package builds geographically-correct SVG maps from JSON.

Example:

```python
import json
from worldly import MapSheet, Stylesheet, Graticule, Scalebar, marshall

with open("world_land.json") as f:
    continents = marshall(json.load(f))

with MapSheet("world_map.svg", projection="Mercator") as mapsheet:
    mapsheet.stylesheet = Stylesheet("style.css")
    mapsheet.add(continents)
    mapsheet.add(Graticule())
    mapsheet.add(Scalebar("lower right"))
```

Generates the following image:

![](example.svg)


Maps can be bound to data to create chloropleth maps:

```python
import json
from worldly import MapSheet, marshall

with open("states.json") as f:
    states = marshall(json.load(f))

with MapSheet("world_map.svg", projection="USA-albers") as mapsheet:
    mapsheet.add(states, fill_color="pop_dens_2010", edge_color="none")
```

![](example_pop.svg)

