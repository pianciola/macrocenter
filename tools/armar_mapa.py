"""Arma assets/provincias.geojson: los polígonos oficiales de las provincias (IGN, Instituto Geográfico Nacional),
simplificados para que pesen poco. Se corre a mano, una sola vez (los límites no cambian):

    pip install shapely
    python tools/armar_mapa.py

Tierra del Fuego queda con las islas Malvinas, la isla de los Estados y Tierra del Fuego. La Antártida y las islas del
Atlántico Sur (Georgias, Sandwich), que el IGN también incluye en esa provincia, no se dibujan: harían el mapa inútil.
"""
import json
import sys
from pathlib import Path

import requests
from shapely.geometry import MultiPolygon, mapping, shape

URL = ("https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ign:provincia"
       "&outputFormat=application/json&srsName=EPSG:4326")
TOLERANCIA = 0.02   # grados (~2 km)
AREA_MINIMA = 0.01  # grados²: islas más chicas no se dibujan
SALIDA = Path(__file__).resolve().parent.parent / "assets" / "provincias.geojson"

# nombre en el IGN -> (id, nombre que se muestra)
NOMBRES = {"Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Tierra del Fuego"}


def main() -> int:
    g = requests.get(URL, timeout=300).json()
    out = []
    for f in g["features"]:
        nombre = NOMBRES.get(f["properties"]["nam"], f["properties"]["nam"])
        geom = shape(f["geometry"])
        polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        if nombre == "Tierra del Fuego":  # solo el archipiélago y Malvinas (lat > -56, lon entre -75 y -56)
            polys = [p for p in polys if p.bounds[0] > -75 and p.bounds[2] < -56 and p.bounds[1] > -56]
        polys = [p for p in polys if p.area >= AREA_MINIMA]
        geom = MultiPolygon(polys).simplify(TOLERANCIA, preserve_topology=True)
        geom = geom if isinstance(geom, MultiPolygon) else MultiPolygon([geom])
        coords = [[[[round(x, 3), round(y, 3)] for x, y in ring.coords] for ring in [poly.exterior, *poly.interiors]]
                  for poly in geom.geoms]
        out.append({"type": "Feature", "id": nombre, "properties": {"nombre": nombre},
                    "geometry": {"type": "MultiPolygon", "coordinates": coords}})
    SALIDA.write_text(json.dumps({"type": "FeatureCollection", "features": out}, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    print(f"{len(out)} provincias, {SALIDA.stat().st_size / 1e3:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
