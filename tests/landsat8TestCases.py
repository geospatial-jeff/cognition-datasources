import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources

class Landsat8TestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('Landsat8')
        self.geoj = {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -96.84173583984374,
              32.713355353177555
            ],
            [
              -96.63848876953125,
              32.713355353177555
            ],
            [
              -96.63848876953125,
              32.88189375925038
            ],
            [
              -96.84173583984374,
              32.88189375925038
            ],
            [
              -96.84173583984374,
              32.713355353177555
            ]
          ]
        ]
      }
    }
        self.temporal = ("2017-01-01", "2017-12-31")
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])

    def test_manifest_load(self):
        # Confirming loading datasoures into manifest
        self.assertEqual(list(self.manifest), ['Landsat8'])
        self.assertEqual(type(self.manifest['Landsat8']), sources.Landsat8)

    def test_landsat8_pattern(self):
        # Confirming the datasources follows the required pattern
        self.assertEqual(hasattr(self.manifest['Landsat8'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['Landsat8'], 'search'), True)
        self.assertEqual(self.manifest['Landsat8'].stac_compliant, True)

    def test_landsat8_search(self):
        self.manifest.flush()

        self.manifest['Landsat8'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 1)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.Landsat8)

    def test_landsat8_spatial_search(self):
        self.manifest.flush()
        self.manifest['Landsat8'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(response['Landsat8']['meta']['found'], 315)

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['Landsat8']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['Landsat8']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_naip_spatio_temporal_search(self):
        self.manifest.flush()

        self.manifest['Landsat8'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # confirming dates of returned items are within temporal range (2017):
        for feat in response['Landsat8']['features']:
            acquisition_date = feat['properties']['datetime']
            self.assertEqual(acquisition_date.split('-')[0], "2017")

    def test_naip_spatio_temporal_properties_search(self):
        self.manifest.flush()
        # Querying with 'eo:cloud_cover'
        self.manifest['Landsat8'].search(self.geoj['geometry'], properties={'eo:cloud_cover': {'lt': 5}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:cloud_cover'] < 5, True) for feat in response['Landsat8']['features']]

        # Querying with `landsat:processing_level
        self.manifest['Landsat8'].search(self.geoj['geometry'], properties={'landsat:processing_level': {'eq': 'L1TP'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['landsat:processing_level'], 'L1TP') for feat in response['Landsat8']['features']]

    def test_landsat8_search_kwargs(self):
        self.manifest.flush()
        self.manifest['Landsat8'].search(self.geoj['geometry'], limit=30)
        response = self.manifest.execute()
        self.assertEqual(response['Landsat8']['meta']['limit'], '30')