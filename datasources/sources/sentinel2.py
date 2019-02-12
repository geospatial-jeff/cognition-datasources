import json
import requests
import copy

import utm

from datasources.stac.query import STACQuery
from .base import Datasource


class Sentinel2(Datasource):

    def __init__(self, manifest):
        super().__init__(manifest)
        self.endpoint = 'https://sat-api-dev.developmentseed.org/stac/search/'
        self.stac_compliant = True

    def search(self, spatial, temporal=None, properties=None, **kwargs):
        stac_query = STACQuery(spatial, temporal)

        query_body = {'query': {'eo:platform': {'eq': 'sentinel-2a'}},
                      'intersects': json.dumps({
                          "type": "Feature",
                          "properties": {},
                          "geometry": stac_query.spatial
                      })}

        if temporal:
            query_body.update({'time': "/".join([x.strftime("%Y-%m-%dT%H:%M:%S.%fZ") for x in stac_query.temporal])})

        if properties:
            for (k,v) in properties.items():
                query_body['query'].update({k:v})

        if 'limit' in kwargs:
            query_body.update({'limit': kwargs['limit'] / 2})

        # Perform same query for sentinel-2a and sentinel-2b
        query_2b = copy.deepcopy(query_body)
        query_2b['query']['eo:platform']['eq'] = 'sentinel-2b'
        query_2b['query'] = json.dumps(query_2b['query'])
        self.manifest.searches.append([self, query_2b])

        query_body['query'] = json.dumps(query_body['query'])
        self.manifest.searches.append([self, query_body])

    def execute(self, query):
        headers = {
            "ContentType": "application/json",
            "Accept": "application/geo+json"
        }
        r = requests.get(self.endpoint, params=query, headers=headers)

        stac_items = r.json()
        for feat in stac_items['features']:
            # Find EPSG of WGS84 UTM zone from centroid of bbox
            centroid = [(feat['bbox'][1] + feat['bbox'][3]) / 2, (feat['bbox'][0] + feat['bbox'][2]) / 2]
            utm_zone = utm.from_latlon(*centroid)
            epsg = '32' + '5' + str(utm_zone[2]) if centroid[0] < 0 else '32' + '6' + str(utm_zone[2])
            feat['properties'].update({'eo:epsg': int(epsg)})

        return stac_items