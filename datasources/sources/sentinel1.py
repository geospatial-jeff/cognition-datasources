import os

from .base import Datasource
from datasources.stac.query import STACQuery
from sentinelsat.sentinel import SentinelAPI
import utm

from datasources.stac.item import STACItem

"""Mappings between API and STAC attributes"""
stac_to_api = {
    'sar:polarization': lambda n: {'polarisationmode': ' '.join(n['sar:polarization']['eq'])},
    'sar:absolute_orbit': lambda n: {'orbitnumber': n['sar:absolute_orbit']['eq']},
    'sar:type': lambda n: {'producttype': n['sar:type']['eq']},
    'sar:instrument_mode': lambda n: {'sensoroperationalmode': n['sar:instrument_mode']['eq']},
    'eo:epsg': lambda n: {'epsg': n['eo:epsg']['eq']},
    'legacy:lastorbitnumber': lambda n: {'lastorbitnumber': n['legacy:lastorbignumber']['eq']},
    'legacy:swathidentifier': lambda n: {'swathidentifier': n['legacy:swathidentifier']}
}

api_to_stac = {
    'beginposition': lambda n: {'dr:start_datetime': n['beginposition'], 'datetime': n['beginposition']},
    'endposition': lambda n: {'dr:end_position': n['endposition']},
    'platformname': lambda n: {'sar:platform': n['platformname'] + n['title'][2], 'sar:constellation': n['platformname']},
    'instrumentname': lambda n: {"sar:instrument": n['instrumentname']},
    'sensoroperationalmode': lambda n: {"sar:instrument_mode": n['sensoroperationalmode']},
    'instrumentshortname': lambda n: {"sar:frequency_band": n["instrumentshortname"][4]},
    'polarisationmode': lambda n: {"sar:polarization": n["polarisationmode"].split(' ')},
    'orbitdirection': lambda n: {"sar:pass_direction": n["orbitdirection"].lower()},
    'producttype': lambda n: {"sar:type": n['producttype']},
    'link_icon': lambda n: {"asset_thumbnail": {"href": n['link_icon'], "title": "Thumbnail"}},
    'link': lambda n: {"asset_analytic": {"href": n['link'], "title": "SAR Asset"}},
    'id': lambda n: {"id": n['id']},
    'swathidentifier': lambda n: {"legacy:swathidentifier": n['swathidentifier']},
    'lastorbitnumber': lambda n: {"legacy:lastorbitnumber": n['lastorbitnumber']}
}


class Sentinel1(Datasource):

    def __init__(self, manifest):
        super().__init__(manifest)
        self.api = SentinelAPI(os.getenv('COPERNICUS_USER'), os.getenv('COPERNICUS_PASSWORD'))
        self.api.api_url = "https://scihub.copernicus.eu/dhus/"

    def search(self, spatial, temporal=None, properties=None, **kwargs):
        stac_query = STACQuery(spatial, temporal)

        query_body = {'area': stac_query.wkt(),
                      'limit': 10,
                      'platformname': 'Sentinel-1',
                      }

        if temporal:
            query_body.update({'date': stac_query.temporal})

        if properties:
            api_props = {}
            for prop in properties:
                api_props.update(stac_to_api[prop](properties))
            query_body.update(api_props)

        if 'limit' in kwargs:
            query_body.update({'limit': kwargs['limit']})

        self.manifest.searches.append([self,query_body])

    def execute(self, query):
        epsg_check = query.pop('epsg') if 'epsg' in list(query) else None
        products = self.api.query(**query)
        response = self.api.to_geojson(products)

        stac_items = {
            "type": "FeatureCollection",
            "features": []
        }

        for feat in response['features']:
            stac_props = {}

            # Calculate bbox from coords
            xcoords = [x[0] for x in feat['geometry']['coordinates'][0]]
            ycoords = [y[1] for y in feat['geometry']['coordinates'][0]]
            feat.update({"bbox": [min(xcoords), min(ycoords), max(xcoords), max(ycoords)]})

            # Find EPSG of WGS84 UTM zone from centroid of bbox
            centroid = [(feat['bbox'][1] + feat['bbox'][3]) / 2, (feat['bbox'][0] + feat['bbox'][2]) / 2]
            utm_zone = utm.from_latlon(*centroid)
            epsg = '32' + '5' + str(utm_zone[2]) if centroid[0] < 0 else '32' + '6' + str(utm_zone[2])
            stac_props.update({'eo:epsg': int(epsg)})

            if epsg_check:
                if int(epsg) != epsg_check:
                    continue

            # Replace properties with STAC properties
            for prop in feat['properties']:
                if prop in list(api_to_stac):
                    stac_props.update(api_to_stac[prop](feat['properties']))
            feat['properties'] = stac_props

            # Move assets from properties to feature
            feat.update({"assets": {"analytic": feat['properties'].pop("asset_analytic"),
                                    "thumbnail": feat['properties'].pop("asset_thumbnail")}})

            # Update ID
            feat.update({"id": stac_props.pop("id")})

            # Validate STAC item
            STACItem.load(feat)
            stac_items['features'].append(feat)

        return stac_items





        # for feat in response['features']:
        #     properties = feat['properties']
        #     stac_props = {}
        #     for prop in properties:
        #         if prop in list(api_to_stac):
        #             stac_props.update(api_to_stac[prop](properties))
        #
        #
        #     # Replace properties with new STAC properties
        #     feat['properties'] = stac_props
        #
        #     # Move assets from properties to feature
        #     feat.update({"assets": {"analytic": stac_props.pop("asset_analytic"),
        #                             "thumbnail": stac_props.pop("asset_thumbnail")}})
        #
        #     # Update ID
        #     feat.update({"id": stac_props.pop("id")})
        #
        #     # Calculate bbox from coords
        #     xcoords = [x[0] for x in feat['geometry']['coordinates'][0]]
        #     ycoords = [y[1] for y in feat['geometry']['coordinates'][0]]
        #     feat.update({"bbox": [min(xcoords), min(ycoords), max(xcoords), max(ycoords)]})
        #
        #     # Find EPSG of WGS84 UTM zone from centroid of bbox
        #     centroid = [(feat['bbox'][1] + feat['bbox'][3]) / 2, (feat['bbox'][0] + feat['bbox'][2]) / 2]
        #     utm_zone = utm.from_latlon(*centroid)
        #     epsg = '32' + '5' + str(utm_zone[2]) if centroid[0] < 0 else '32' + '6' + str(utm_zone[2])
        #     feat['properties'].update({'eo:epsg': int(epsg)})
        #
        #     if epsg_check:
        #         if epsg_check != int(epsg):
        #             print("Bad EPSG: {}".format(epsg))
        #             continue
        #
        #     # Validate the STAC item
        #     STACItem.load(feat)
        #     stac_items['features'].append(feat)

        return stac_items