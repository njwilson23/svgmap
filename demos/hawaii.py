import worldly

style = ".land { fill: #333333; }"

with worldly.MapSheet("hawaii_scale.svg", scale=1/600.0) as mapsheet:
    mapsheet.style = style
    mapsheet.add_geojson_file("demos/hawaii.geojson", class_name="land")

with worldly.MapSheet("hawaii_bbox.svg", bbox=(-162, 17, -153, 24)) as mapsheet:
    mapsheet.style = style
    mapsheet.add_geojson_file("demos/hawaii.geojson", class_name="land")

