import worldly
from worldly.projection import SouthPolarStereographic

with worldly.MapSheet("antarctica.svg", bbox=(-135, -50, 45, -50),
            projection=SouthPolarStereographic) as mapsheet:

    mapsheet.style = """
    .ice { fill: #AAAAAA;
           stroke: #AAAAAA;
           stroke-width: 0.8; }
    .shelf { fill: steelblue;
             stroke: steelblue;
             stroke-width: 0.1;
             opacity: 0.2; }
    """

    mapsheet.add_geojson_file("tests/antarctica.geojson", class_name="ice")
    mapsheet.add_geojson_file("tests/antarctica_ice_shelves.geojson", class_name="shelf")

