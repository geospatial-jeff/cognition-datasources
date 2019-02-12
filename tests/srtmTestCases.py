import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources

class SRTMTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('SRTM')
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
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])

    def test_manifest_load(self):
        self.assertEqual(list(self.manifest), ['SRTM'])
        self.assertEqual(type(self.manifest['SRTM']), sources.SRTM)

    def test_elev_tiles_pattern(self):
        self.assertEqual(hasattr(self.manifest['SRTM'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['SRTM'], 'search'), True)
        self.assertEqual(self.manifest['SRTM'].stac_compliant, False)

    def test_elev_tiles_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['SRTM'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 1)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.SRTM)

    def test_elev_tiles_spatial_search(self):
        self.manifest.flush()
        self.manifest['SRTM'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['SRTM'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['SRTM']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['SRTM']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)