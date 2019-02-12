import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources


class CBERSTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('CBERS')
        self.geoj =  {
                      "type": "Feature",
                      "properties": {},
                      "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                          [
                            [
                              -64.951171875,
                              -7.520426889868663
                            ],
                            [
                              -64.5172119140625,
                              -7.520426889868663
                            ],
                            [
                              -64.5172119140625,
                              -7.144498849647323
                            ],
                            [
                              -64.951171875,
                              -7.144498849647323
                            ],
                            [
                              -64.951171875,
                              -7.520426889868663
                            ]
                          ]
                        ]
                      }
                    }
        self.temporal = ("2016-01-01", "2016-12-31")
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])

    def test_manifest_load(self):
        # Confirming loading datasources into manifest
        self.assertEqual(list(self.manifest), ['CBERS'])
        self.assertEqual(type(self.manifest['CBERS']), sources.CBERS)

    def test_cbers_pattern(self):
        self.assertEqual(hasattr(self.manifest['CBERS'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['CBERS'], 'search'), True)
        self.assertEqual(self.manifest['CBERS'].stac_compliant, False)

    def test_cbers_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['CBERS'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 3)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.CBERS)

    def test_cbers_spatial_search(self):
        self.manifest.flush()
        self.manifest['CBERS'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['CBERS'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['CBERS']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['CBERS']['features']:
            asset_geom = Polygon([[feat['bbox'][0], feat['bbox'][3]],
                                  [feat['bbox'][2], feat['bbox'][3]],
                                  [feat['bbox'][2], feat['bbox'][1]],
                                  [feat['bbox'][0], feat['bbox'][1]],
                                  [feat['bbox'][0], feat['bbox'][3]]])

            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_cbers_spatio_temporal_search(self):
        self.manifest.flush()
        self.manifest['CBERS'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # Confirming dates of returned items are within temporal range (2017)
        for feat in response['CBERS']['features']:
            acquisition_date = feat['properties']['datetime']
            self.assertEqual(acquisition_date.split('-')[0], "2016")

    def test_cbers_spatio_temporal_properties_search(self):
        # Querying with eo:instrument
        self.manifest.flush()
        self.manifest['CBERS'].search(self.geoj['geometry'], properties={'eo:instrument': {'eq': 'PAN10M'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:instrument'], 'PAN10M') for feat in response['CBERS']['features']]

        # Querying with eo:sun_azimuth
        self.manifest.flush()
        self.manifest['CBERS'].search(self.geoj['geometry'], properties={'eo:sun_azimuth': {'lt': 35}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:sun_azimuth'] < 35, True) for feat in response['CBERS']['features']]

        # Querying with eo:gsd
        self.manifest.flush()
        self.manifest['CBERS'].search(self.geoj['geometry'], properties={'eo:gsd': {'lt': 5}, 'eo:instrument': {'eq': 'PAN5M'}})
        response = self.manifest.execute()
        self.assertEqual(len(response['CBERS']['features']), 0)