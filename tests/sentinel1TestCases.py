import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources


class Sentinel1TestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('Sentinel1')
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
        self.assertEqual(list(self.manifest), ['Sentinel1'])
        self.assertEqual(type(self.manifest['Sentinel1']), sources.Sentinel1)

    def test_sentinel_pattern(self):
        self.assertEqual(hasattr(self.manifest['Sentinel1'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['Sentinel1'], 'search'), True)
        self.assertEqual(self.manifest['Sentinel1'].stac_compliant, False)

    def test_sentinel_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['Sentinel1'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 1)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.Sentinel1)

    def test_sentinel_spatial_search(self):
        self.manifest.flush()
        self.manifest['Sentinel1'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['Sentinel1'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['Sentinel1']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['Sentinel1']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_sentinel_spatio_temporal_search(self):
        self.manifest.flush()
        self.manifest['Sentinel1'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # Confirming dates of returned items are within temporal range (2017)
        for feat in response['Sentinel1']['features']:
            acquisition_date = feat['properties']['datetime']
            self.assertEqual(acquisition_date.split('-')[0], "2017")

    def test_sentinel_spatio_temporal_properties_search(self):
        # Querying with sar:polarization
        self.manifest.flush()
        self.manifest['Sentinel1'].search(self.geoj['geometry'], properties={'sar:polarization': {'eq': ['VV', 'VH']}})
        response = self.manifest.execute()
        for feat in response['Sentinel1']['features']:
            self.assertEqual('VV' in feat['properties']['sar:polarization'], True)
            self.assertEqual('VH' in feat['properties']['sar:polarization'], True)

        # Querying with sar:instrument_mode
        self.manifest['Sentinel1'].search(self.geoj['geometry'], properties={'sar:instrument_mode': {'eq': 'IW'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['sar:instrument_mode'], 'IW') for feat in response['Sentinel1']['features']]

    def test_sentinel_epsg_search(self):
        self.manifest.flush()
        # Querying with eo:epsg
        self.manifest['Sentinel1'].search(self.geoj['geometry'], properties={'eo:epsg': {'eq': 32613}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:epsg'], 32613) for feat in response['Sentinel1']['features']]

    def test_sentinel_search_kwargs(self):
        self.manifest.flush()
        self.manifest['Sentinel1'].search(self.geoj['geometry'], limit=20)
        response = self.manifest.execute()
        self.assertEqual(len(response['Sentinel1']['features']), 20)
