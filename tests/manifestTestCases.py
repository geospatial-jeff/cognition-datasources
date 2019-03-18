import unittest
from datasources import Manifest
from datasources.sources import collections

class ManifestTestCases(unittest.TestCase):

    valid_sources = ["CBERS", "Landsat8", "Sentinel1", "Sentinel2", "NAIP", "SRTM", "ElevationTiles"]

    def setUp(self):
        self.manifest = Manifest()
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
        self.temporal = ("2016-01-01", "2016-12-31")


    def test_load_sources(self):
        self.assertEqual(list(self.manifest).sort(), [x.__name__ for x in collections.all].sort())

    def test_spatial_query(self):
        self.manifest.flush()
        for s in self.manifest.sources:
            s.search(self.geoj['geometry'])

        response = self.manifest.execute()
        self.assertEqual(list(response), self.valid_sources)

        expected_counts = [29, 10, 10, 10, 10, 1, 4]
        counts = [len(response[item]['features']) for item in response]
        self.assertListEqual(counts, expected_counts)

    def test_spatio_temporal_query(self):
        self.manifest.flush()
        for s in self.manifest.sources:
            s.search(self.geoj['geometry'], temporal=self.temporal)

        response = self.manifest.execute()

        for item in response:
            for feat in response[item]['features']:
                if feat['properties']['datetime']:
                    if feat['properties']['datetime'] != 'null':
                        self.assertEqual(feat['properties']['datetime'].split('-')[0], '2016')