import os
import math
import operator

from .base import Datasource
from stac.query import STACQuery


class SRTM(Datasource):

    def __init__(self, manifest):
        super().__init__(manifest)
        self.endpoint = 'https://s3.amazonaws.com/elevation-tiles-prod/skadi'

    def check_properties(self, asset, properties):
        for item in properties:
            equality = next(iter(properties[item]))
            comparison_operator = getattr(operator, equality)
            if not comparison_operator(asset[item], properties[item][equality]):
                return False
        return True

    def search(self, spatial, temporal=None, properties=None, **kwargs):
        stac_query = STACQuery(spatial, temporal)
        bbox = stac_query.bbox()
        if (bbox[2] - bbox[0]) < 1:
            xrange = [math.floor(bbox[0])]
        else:
            xrange = list(range(math.floor(bbox[0]), math.ceil(bbox[2])))
        if (bbox[3] - bbox[1]) < 1:
            yrange = [math.floor(bbox[1])]
        else:
            yrange = list(range(math.floor(bbox[1]), math.ceil(bbox[3])))

        for x in xrange:
            if -10 < x < 0:
                xtile = 'W00'+str(abs(x))
            elif x <= -10:
                xtile = 'W'+str(abs(x))
            elif 10 > x > 0:
                xtile = 'E00'+str(x)
            elif x >= 10:
                xtile = 'E'+str(x)
            else:
                xtile = 'E0'

            for y in yrange:
                if -10 < y < 0:
                    ytile = 'S0' + str(abs(y))
                elif y <= -10:
                    ytile = 'S' + str(abs(y))
                elif 10 > y > 0:
                    ytile = 'N0' + str(y)
                elif y >= 10:
                    ytile = 'N' + str(y)
                else:
                    ytile = 'S0'

                xmax = x + 1
                ymax = y + 1

                query_body = {
                    'xtile': xtile,
                    'ytile': ytile,
                    'res': 30.0,
                    'epsg': 4326,
                    'asset_link': os.path.join(self.endpoint, ytile, f"{ytile}{xtile}.hgt.gz"),
                    'source': 'srtm',
                    'bbox': [x, y, xmax, ymax],
                    'coordinates': [[[x, ymax], [xmax, ymax], [xmax, y], [x, y], [x, ymax]]]
                }

                if properties:
                    query_body.update({'properties': properties})

                self.manifest.searches.append([self, query_body])

    def execute(self, query):
        stac_item = {
            'id': f"{query['source']}-skadi-{query['xtile']}-{query['ytile']}",
            'type': 'Feature',
            'bbox': query['bbox'],
            'geometry': {
                'type': 'Polygon',
                'coordinates': query['coordinates']
            },
            'properties': {
                'datetime': None,
                'eo:gsd': query['res'],
                'eo:epsg': query['epsg'],
                'eo:instrument': query['source'],
                'legacy:xtile': query['xtile'],
                'legacy:ytile': query['ytile'],
            },
            "assets": {
                "tile": {
                    "href": query['asset_link'],
                    "title": "SRTM Skadi Tile"
                }
            }
        }

        if 'properties' in list(query):
            if not self.check_properties(stac_item['properties'], query['properties']):
                return None

        return stac_item
