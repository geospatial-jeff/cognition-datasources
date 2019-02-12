import os
import operator

import mercantile
import requests

from .base import Datasource
from datasources.stac.query import STACQuery

class ElevationTiles(Datasource):

    @staticmethod
    def tile_resolution(tile):
        bounds = mercantile.xy_bounds(tile)
        xres = (bounds.right - bounds.left) / 512
        yres = (bounds.right - bounds.left) / 512
        return (xres + yres) / 2

    @staticmethod
    def tile_bbox(tile):
        bounds = mercantile.bounds(tile)
        return [bounds.west, bounds.south, bounds.east, bounds.north]

    @staticmethod
    def tile_source(headers):
        dem_sources = [x.replace(' ', '').split('/')[0] for x in headers['x-amz-meta-x-imagery-sources'].split(',')]
        majority_source = max(set(dem_sources), key=dem_sources.count)
        return majority_source

    def __init__(self, manifest):
        super().__init__(manifest)
        self.endpoint = 'https://s3.amazonaws.com/elevation-tiles-prod/geotiff/'

    def check_properties(self, asset, properties):
        for item in properties:
            equality = next(iter(properties[item]))
            comparison_operator = getattr(operator, equality)
            if not comparison_operator(asset[item], properties[item][equality]):
                return False
        return True

    def search(self, spatial, temporal=None, properties=None, **kwargs):
        stac_query = STACQuery(spatial, temporal)

        if 'zoom' in kwargs:
            zoom = kwargs['zoom']
        else:
            zoom = 8

        tiles = mercantile.tiles(*stac_query.bbox(), zoom)

        if 'limit' in kwargs:
            tiles = list(tiles)[:kwargs['limit']]

        for tile in tiles:
            query_body = {'res': self.tile_resolution(tile),
                          'asset_link': os.path.join(self.endpoint, str(tile.z), str(tile.x), str(tile.y)+'.tif'),
                          'bbox': self.tile_bbox(tile),
                          'epsg': 3857,
                          'x': tile.x,
                          'y': tile.y,
                          'z': tile.z
                          }

            if properties:
                query_body.update({'properties': properties})

            self.manifest.searches.append([self, query_body])

    def execute(self, query):
        r = requests.head(query['asset_link'])
        source = self.tile_source(r.headers)

        stac_item = {
            "id": f"{source}-{query['z']}-{query['x']}-{query['y']}",
            "type": "Feature",
            "bbox": query['bbox'],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [query['bbox'][0], query['bbox'][3]],
                        [query['bbox'][2], query['bbox'][3]],
                        [query['bbox'][2], query['bbox'][1]],
                        [query['bbox'][0], query['bbox'][1]],
                        [query['bbox'][0], query['bbox'][3]]
                    ]
                ]
            },
            "properties": {
                "datetime": None,
                "eo:gsd": query['res'],
                "eo:epsg": query['epsg'],
                "eo:instrument": source,
                "legacy:x": query['x'],
                "legacy:y": query['y'],
                "legacy:z": query['z']
            },
            "assets": {
                "tile": {
                    "href": query['asset_link'],
                    "title": "Digital Elevation Tiles"
                }
            }
        }

        if 'properties' in list(query):
            if not self.check_properties(stac_item['properties'], query['properties']):
                return None

        return stac_item

