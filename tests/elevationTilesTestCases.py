import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources

class ElevationTilesTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source('ElevationTiles')
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
        self.assertEqual(list(self.manifest), ['ElevationTiles'])
        self.assertEqual(type(self.manifest['ElevationTiles']), sources.ElevationTiles)

    def test_elev_tiles_pattern(self):
        self.assertEqual(hasattr(self.manifest['ElevationTiles'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['ElevationTiles'], 'search'), True)
        self.assertEqual(self.manifest['ElevationTiles'].stac_compliant, False)

    def test_elev_tiles_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['ElevationTiles'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 4)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.ElevationTiles)

    def test_elev_tiles_spatial_search(self):
        self.manifest.flush()
        self.manifest['ElevationTiles'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['ElevationTiles'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['ElevationTiles']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['ElevationTiles']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertEqual(asset_geom.intersects(self.geoj_geom), True)

    def test_elev_tiles_spatial_properties_search(self):
        # Querying with eo:instrument
        self.manifest['ElevationTiles'].search(self.geoj['geometry'], properties={'eo:instrument': {'eq': 'srtm'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:instrument'], 'srtm') for feat in response['ElevationTiles']['features']]

        # Querying with eo:resolution
        self.manifest['ElevationTiles'].search(self.geoj['geometry'], properties={'eo:gsd': {'lt': 310}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['eo:gsd'] < 310, True) for feat in response['ElevationTiles']['features']]

    def test_elev_tiles_search_kwargs(self):
        self.manifest['ElevationTiles'].search(self.geoj['geometry'], limit=10, zoom=14)
        response = self.manifest.execute()
        self.assertEqual(len(response['ElevationTiles']['features']), 10)
        [self.assertEqual(feat['properties']['legacy:z'], 14) for feat in response['ElevationTiles']['features']]