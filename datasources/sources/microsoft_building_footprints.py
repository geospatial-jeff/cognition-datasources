import json

import requests

from .base import Datasource
from datasources.stac.query import STACQuery

symbols = {
    'eq': '=',
    'lt': '<',
    'gt': '>',
    'lte': '<=',
    'gte': '>='
}

class MicrosoftBuildingFootprints(Datasource):

    def __init__(self, manifest):
        super().__init__(manifest)
        self.endpoint = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/MSBFP2/FeatureServer/0/query'

    def search(self, spatial, temporal=None, properties=None, limit=1000, **kwargs):
        stac_query = STACQuery(spatial, temporal)

        query_body = {
            'geometry': json.dumps({"rings": stac_query.spatial['coordinates']}),
            'geometryType': 'esriGeometryPolygon',
            'inSR': 4326,
            'outSR': 4326,
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',
            'returnGeometry': 'true',
            'returnZ': 'false',
            'returnM': 'false',
            'f': 'pgeojson',
        }

        where = ''

        if properties:
            for item in properties:
                if item == 'eo:epsg':
                    query_body['outSR'] = properties['eo:epsg']['eq']
                elif item == 'legacy:area' or item == 'legacy:length' or item == 'legacy:state':
                    equality = list(properties[item])[0]
                    if item == 'legacy:area':
                        query_string = "Shape__Area{}{}".format(symbols[equality], properties[item][equality])
                    elif item == 'legacy:length':
                        query_string = "Shape__Length{}{}".format(symbols[equality], properties[item][equality])
                    elif item == 'legacy:state':
                        query_string = "StateAbbrev='{}'".format(properties[item][equality])
                    if len(where) > 0:
                        where += " AND " + query_string
                    else:
                        where += query_string

        query_body.update({'where': where})

        if limit <= 2000:
            self.manifest.searches.append([self, query_body])
        else:
            query_body.update({'returnIdsOnly': 'true',
                               'returnUniqueIdsOnly': 'true'})
            response = self.execute(query_body, objectid=True)
            print(response)

            feature_query = {'where': query_body['where'],
                             'objectIds': response['properties']['objectIds'],
                             'outSR': query_body['outSR'],
                             'outFields': '*',
                             'returnGeometry': 'true',
                             'returnZ': 'false',
                             'returnM': 'false',
                             'f': 'pgeojson'
                             }

            self.manifest.searches.append([self, feature_query])

    def execute(self, query, objectid=False):
        r = requests.get(self.endpoint, params=query)
        data = r.json()

        for feat in data['features']:
            stac_properties = {
                "eo:epsg": query['outSR'],
                "legacy:area": feat['properties']['Shape__Area'],
                "legacy:length": feat['properties']['Shape__Length'],
                "legacy:objectid": feat['properties']['OBJECTID'],
                "legacy:state": feat['properties']['StateAbbrev'],
                "legacy:block_group_id": feat['properties']['BlockgroupID']
            }
            feat['properties'] = stac_properties

            xvals = [x[0] for x in feat['geometry']['coordinates'][0]]
            yvals = [y[1] for y in feat['geometry']['coordinates'][0]]
            feat.update({'bbox': [min(xvals), min(yvals), max(xvals), max(yvals)]})

        if objectid:
            return data
        else:
            return data['features']