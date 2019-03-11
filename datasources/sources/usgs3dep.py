import json
import os
import uuid
import operator

import boto3
from rtree import index

from datasources.stac.query import STACQuery
from datasources.stac.item import STACItem
from .base import Datasource

try:
    rtree_location = os.environ['3DEP_RTREE_LOCATION']
except KeyError:
    rtree_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', '3dep/3dep_rtree')

client = boto3.client('s3')
bucket = 'usgs-lidar-public'

class USGS3DEP(Datasource):

    tags = ['Elevation', 'Raster']

    @staticmethod
    def query_3dep_reference(bbox):
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
        names = []
        stac_query = STACQuery(spatial, temporal)
        projects = self.query_3dep_reference(stac_query.bbox())[:limit]
        for item in projects:
            if item['project_name'] not in names:
            # Temporal check by checking year of start/end date
                if temporal and item['year']:
                    if stac_query.temporal[0].year == item['year'] or stac_query.temporal[1].year == item['year']:
                        if properties:
                            item.update({'properties': properties})
                        self.manifest.searches.append([self, item])
                        names.append(item['project_name'])
                else:
                    self.manifest.searches.append([self, item])
                    names.append(item['project_name'])

    def execute(self, query):
        # Download metadata from query item
        response = client.get_object(Bucket=bucket, Key=os.path.join(query['project_name'], 'ept.json'))
        metadata = json.loads(response['Body'].read().decode('utf-8'))

        stac_item = {
            'id': str(uuid.uuid4()),
            'type': 'Feature',
            'geometry': json.loads(query['geom']),
            'properties': {
                'datetime': f"{query['year']}-01-01T00:00:00.00Z",
                'eo:epsg': metadata['srs']['horizontal'],
                'pc:count': metadata['points'],
                'pc:type': 'lidar',
                'pc:encoding': metadata['dataType'],
                'pc:schema': metadata['schema'],
                'legacy:span': metadata['span'],
                'legacy:version': metadata['version'],
            },
            'assets': {
                's3path': {
                    'href': f"s3://{bucket}/{query['project_name']}",
                    'title': 'EPT data'
                }
            },
        }

        if "properties" in list(query):
            if self.check_properties(stac_item['properties'], query['properties']):
                return [stac_item]
        else:
            return [stac_item]