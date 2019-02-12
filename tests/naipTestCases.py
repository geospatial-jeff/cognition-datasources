import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources

class NAIPTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('NAIP')
        self.geoj = {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                          -101.28433227539062,
                          46.813218976041945
                        ],
                        [
                          -100.89431762695312,
                          46.813218976041945
                        ],
                        [
                          -100.89431762695312,
                          47.06450941441436
                        ],
                        [
                          -101.28433227539062,
                          47.06450941441436
                        ],
                        [
                          -101.28433227539062,
                          46.813218976041945
                        ]
                      ]
                    ]
                  }
                }
        self.temporal = ("2017-01-01", "2017-12-31")
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])

    def test_manifest_load(self):
        # Confirming loading datasources into manifest
        self.assertEqual(list(self.manifest), ['NAIP'])
        self.assertEqual(type(self.manifest['NAIP']), sources.NAIP)

    def test_naip_pattern(self):
        # Confirming that datasource follows the required pattern
        self.assertEqual(hasattr(self.manifest['NAIP'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['NAIP'], 'search'), True)
        self.assertEqual(self.manifest['NAIP'].stac_compliant, False)

    def test_naip_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['NAIP'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 175)

        self.assertEqual(type(self.manifest.searches[0][0]), sources.NAIP)
        self.assertEqual(list(self.manifest.searches[0][1]), ['key', 'utm', 'bucket', 'datetime', 'resolution', 'md_key'])

        # Flushing all searches
        self.manifest.flush()

    def test_naip_spatial_search(self):
        self.manifest.flush()
        self.manifest['NAIP'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['NAIP'])

        # Confirming output is a valid feature collection
        # NOTE: Each individual feature is already validated against the STAC spec (see stac/item.py)
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['NAIP']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Copnfirming that each output feature intersects the input
        for feat in response['NAIP']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_naip_spatio_temporal_search(self):
        self.manifest.flush()

        self.manifest['NAIP'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # Confirming dates of returned items are within temporal range (2017)
        for feat in response['NAIP']['features']:
            acquisition_date = feat['properties']['datetime']
            self.assertEqual(acquisition_date.split('-')[0], "2017")

    def test_naip_spatio_temporal_properties_search(self):
        # Querying with 'eo:instrument'
        self.manifest.flush()
        self.manifest['NAIP'].search(self.geoj['geometry'], properties={'eo:instrument': {'eq': 'Leica ADS100'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:instrument'], 'Leica ADS100') for feat in response['NAIP']['features']]

        # Querying with 'eo:gsd'
        self.manifest['NAIP'].search(self.geoj['geometry'], properties={'eo:gsd': {'lt': 1}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:gsd'] <= 1, True) for feat in response['NAIP']['features']]

        # Querying with 'eo:epsg'
        self.manifest['NAIP'].search(self.geoj['geometry'], properties={'eo:epsg': {'eq': '29614'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:epsg'], 26914) for feat in response['NAIP']['features']]

    def test_naip_search_kwargs(self):
        self.manifest.flush()
        self.manifest['NAIP'].search(self.geoj['geometry'], product="visual", limit=1)
        self.manifest['NAIP'].search(self.geoj['geometry'], product="analytic", limit=1)
        self.manifest['NAIP'].search(self.geoj['geometry'], product="raw", limit=1)
        response = self.manifest.execute()
        self.assertEqual(len(response['NAIP']['features']), 3)

        asset_types = [list(item['assets'])[0] for item in response['NAIP']['features']]
        self.assertEqual(asset_types, ['visualization', 'analytic', 'source'])