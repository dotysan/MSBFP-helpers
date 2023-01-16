"""Microsoft building footprints."""

import os
import csv
import gzip
import json
import shutil
import typing

from requests import get as req_get

import mercantile
from shapely.geometry import shape, Polygon


def coords2quadkeys(coords: tuple, level: int = 9) -> list:
    """Returns a list of quadkeys from a GeoJSON geometry.coordinates list."""

    tiles = []
    for point in explode(coords):
        lng, lat = point
        tiles.append(mercantile.tile(lng, lat, level))

    quadkeys = []
    for tile in set(tiles):
        quadkeys.append(mercantile.quadkey(tile))
    return quadkeys


def explode(coords: tuple) -> typing.Iterator[tuple]:
    """Extract all (x,y) tuples from a GeoJSON coordinate-like thing."""

    for e in coords:
        if isinstance(e, (int, float)):
            yield coords
            break
        else:
            for f in explode(e):
                yield f


class MSBFP:
    """Microsoft building footprints."""

    CACHE_DIR = '.msbfp'

    def __init__(self, locations: tuple = None):
        """Build dictionary of quadkey links."""

        self.mskeys = {}

        dsl = 'https://minedbuildings.blob.core.windows.net/global-buildings/dataset-links.csv'
        with req_get(dsl, stream=True) as resp:
            assert resp.status_code == 200

            for row in csv.DictReader(l.decode() for l in resp.iter_lines()):
                if locations:
                    if row['Location'] in locations:
                        self.mskeys[row['QuadKey']] = row['Url']
                else:
                    self.mskeys[row['QuadKey']] = row['Url']

        os.makedirs(MSBFP.CACHE_DIR, exist_ok=True)  # cache downloads

    def buildings(self, quadkeys: list, coords: tuple = None) -> list:
        """Build list of buildings in quadkey list and filter by coordinates."""

        coord_geo = Polygon(coords) if coords else None

        buildings = []
        for quadkey in set(quadkeys):
            url = self.mskeys.get(quadkey)
            if not url:
                print(f"Microsoft doesn't know about any buildings in quadkey {quadkey}.")
                continue

            jsonfile = self.getjson(url)
            with open(jsonfile) as js:
                for line in js:
                    building = json.loads(line)
                    if coord_geo:
                        bldg_geo = shape(building['geometry'])
                        if coord_geo.contains(bldg_geo) or coord_geo.intersects(bldg_geo):
                            buildings.append(building)
                    else:
                        buildings.append(building)

        return buildings

    def getjson(self, url: str) -> str:
        """Fetch Microsoft quadkey JSON file if needed."""

        path = url.split('/')
        gzfile = f"{MSBFP.CACHE_DIR}/{path[-1]}"
        jsonfile = f"{gzfile[:-6]}json"

        if not os.path.exists(jsonfile) or os.stat(jsonfile).st_size == 0:
            with req_get(url, stream=True) as resp:
                assert resp.status_code == 200

                gz = gzip.GzipFile(fileobj=resp.raw)
                with open(jsonfile, 'wb') as js:
                    shutil.copyfileobj(gz, js)

        return jsonfile
