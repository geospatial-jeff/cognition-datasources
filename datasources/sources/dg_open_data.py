import os
import operator
from datetime import datetime
from rtree import index

from .base import Datasource
from datasources.stac.query import STACQuery
from datasources.stac.item import STACItem

try:
    rtree_location = os.environ['DG_OPEN_DATA_RTREE_LOCATION']
except KeyError:
    rtree_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'dg-open-data/dg_open_data')


class DGOpenData(Datasource):

    stac_compliant = False
    tags = ['EO', 'Satellite', 'Raster']

    @staticmethod
    def query_dg_reference(bbox):
        idx = index.Rtree(rtree_location)
        return [x.object for x in idx.intersection(bbox, objects=True)]

    @staticmethod
    def check_properties(asset, properties):
        for item in properties:
            equality = next(iter(properties[item]))
            comparison_operator = getattr(operator, equality)
            if not comparison_operator(asset[item], properties[item][equality]):
                return False
        return True

    def __init__(self, manifest):
        super().__init__(manifest)

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        stac_query = STACQuery(spatial, temporal)
        candidates = self.query_dg_reference(stac_query.bbox())[:limit]
        for item in candidates:
            splits = item['link'].split('/')
            date = splits[-3]
            dt = datetime.strptime(date, '%Y-%m-%d')
            if temporal:
                if not stac_query.check_temporal(dt):
                    continue
            timeframe = splits[-4]
            event_name = splits[-5]
            uid = splits[-2] + '_' + os.path.splitext(splits[-1])[0]

            item.update({'date': date, 'timeframe': timeframe, 'event_name': event_name, 'id': uid})

            if properties:
                item.update({'properties': properties})

            self.manifest.searches.append([self, item])

    def execute(self, query):

        stac_item = {
            'id': query['id'],
            'type': 'Feature',
            'bbox': query['bbox'],
            'geometry': {
                'type': 'Polygon',
                'coordinates': query['geometry']
            },
            'properties': {
                'datetime': "{}T00:00:00.00Z".format(query['date']),
                'eo:epsg': int(query['eo:epsg']),
                'legacy:event_name': query['event_name'],
                'legacy:timeframe': query['timeframe']
            },
            'assets': {
                'data': {
                    'href': query['link'],
                    'title': 'Raster data'
                }
            }
        }

        # Validate item
        STACItem.load(stac_item)

        if "properties" in list(query):
            if self.check_properties(stac_item['properties'], query['properties']):
                return [stac_item]
        else:
            return [stac_item]

    def example(self):
        geoj = {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -120.673828125,
              32.509761735919426
            ],
            [
              -115.1806640625,
              32.509761735919426
            ],
            [
              -115.1806640625,
              36.35052700542763
            ],
            [
              -120.673828125,
              36.35052700542763
            ],
            [
              -120.673828125,
              32.509761735919426
            ]
          ]
        ]
      }

        self.search(geoj)
        response = self.manifest.execute()
        return response