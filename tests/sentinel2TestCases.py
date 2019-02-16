import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources

class Sentinel2TestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('Sentinel2')
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
        self.assertEqual(list(self.manifest), ['Sentinel2'])
        self.assertEqual(type(self.manifest['Sentinel2']), sources.Sentinel2)

    def test_sentinel_pattern(self):
        self.assertEqual(hasattr(self.manifest['Sentinel2'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['Sentinel2'], 'search'), True)
        self.assertEqual(self.manifest['Sentinel2'].stac_compliant, True)

    def test_sentinel_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['Sentinel2'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 2)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.Sentinel2)

    def test_sentinel_spatial_search(self):
        self.manifest.flush()
        self.manifest['Sentinel2'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['Sentinel2'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['Sentinel2']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['Sentinel2']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_sentinel_spatio_temporal_search(self):
        self.manifest.flush()
        self.manifest['Sentinel2'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # Confirming dates of returned items are within temporal range (2017)
        for feat in response['Sentinel2']['features']:
            acquisition_date = feat['properties']['datetime']
            self.assertEqual(acquisition_date.split('-')[0], "2017")

    def test_sentinel_spatio_temporal_properties_search(self):
        # Querying with 'eo:instrument'
        self.manifest.flush()
        self.manifest['Sentinel2'].search(self.geoj['geometry'], properties={'eo:instrument': {'eq': 'MSI'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:instrument'], 'MSI') for feat in response['Sentinel2']['features']]

        # Querying with 'eo:cloud_cover'
        self.manifest.flush()
        self.manifest['Sentinel2'].search(self.geoj['geometry'], properties={'eo:cloud_cover': {'lt': 10}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:cloud_cover'] < 10, True) for feat in response['Sentinel2']['features']]

        # Querying with 'eo:off_nadir'
        self.manifest.flush()
        self.manifest['Sentinel2'].search(self.geoj['geometry'], properties={'eo:off_nadir': {'lt': 5}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:off_nadir'] < 5, True) for feat in response['Sentinel2']['features']]

    def test_sentinel_search_kwargs(self):
        self.manifest.flush()
        self.manifest['Sentinel2'].search(self.geoj['geometry'], limit=20)
        response = self.manifest.execute()
        self.assertEqual(len(response['Sentinel2']['features']), 40)

