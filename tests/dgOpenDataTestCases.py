import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources

class DGOpenDataTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('DGOpenData')
        self.geoj = {
      "type": "Feature",
      "properties": {},
      "geometry": {
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
    }

        self.temporal = ("2018-11-01", "2018-11-20")
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])

    def test_manifest_load(self):
        # Confirming loading datasoures into manifest
        self.assertEqual(list(self.manifest), ['DGOpenData'])
        self.assertEqual(type(self.manifest['DGOpenData']), sources.DGOpenData)

    def test_dg_pattern(self):
        # Confirming the datasources follows the required pattern
        self.assertEqual(hasattr(self.manifest['DGOpenData'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['DGOpenData'], 'search'), True)
        self.assertEqual(self.manifest['DGOpenData'].stac_compliant, False)

    def test_dg_search(self):
        self.manifest.flush()

        self.manifest['DGOpenData'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 10)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.DGOpenData)

    def test_dg_spatial_search(self):
        self.manifest.flush()
        self.manifest['DGOpenData'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(len(response['DGOpenData']['features']), 10)

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['DGOpenData']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['DGOpenData']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_dg_spatio_temporal_search(self):
        self.manifest.flush()

        self.manifest['DGOpenData'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # confirming dates of returned items are within temporal range (2017):
        for feat in response['DGOpenData']['features']:
            acquisition_date = feat['properties']['datetime']
            splits = acquisition_date.split('-')
            self.assertEqual(int(splits[0]), 2018)
            self.assertEqual(int(splits[1]), 11)
            self.assertTrue(20 > int(splits[2].split('T')[0]) > 1)

    def test_dg_spatio_temporal_properties_search(self):
        self.manifest.flush()
        # Querying with 'eo:epsg'
        self.manifest['DGOpenData'].search(self.geoj['geometry'], properties={'eo:epsg': {'eq': 4326}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:epsg'], 4326) for feat in response['DGOpenData']['features']]

        # Querying with 'legacy:event_name'
        self.manifest.flush()
        self.manifest['DGOpenData'].search(self.geoj['geometry'], properties={'legacy:event_name': {'eq': 'california-wildfires'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['legacy:event_name'], 'california-wildfires') for feat in response['DGOpenData']['features']]

    def test_dg_search_kwargs(self):
        self.manifest.flush()
        self.manifest['DGOpenData'].search(self.geoj['geometry'], limit=20)

        response = self.manifest.execute()
        self.assertTrue(len(response['DGOpenData']['features']) <= 20)


