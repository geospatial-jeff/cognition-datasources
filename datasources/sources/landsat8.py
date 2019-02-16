import json
import requests

from datasources.stac.query import STACQuery
from .base import Datasource

class Landsat8(Datasource):

    def __init__(self, manifest):
        super().__init__(manifest)
        self.endpoint = 'https://sat-api-dev.developmentseed.org/stac/search/'
        self.stac_compliant = True

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        stac_query = STACQuery(spatial, temporal)

        query_body = {'query': {'eo:platform': {'eq': 'landsat-8'}},
                      'limit': limit,
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

        query_body['query'] = json.dumps(query_body['query'])
        self.manifest.searches.append([self, query_body])

    def execute(self, query):
        headers = {
            "ContentType": "application/json",
            "Accept": "application/geo+json"
        }
        r = requests.get(self.endpoint, params=query, headers=headers)
        return r.json()