import unittest
from datasources import Manifest

class NAIPTestCases(unittest.TestCase):

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

        for s in self.valid_sources:
            self.manifest.load_source(s)

    def test_load_sources(self):
        self.assertListEqual(list(self.manifest), self.valid_sources)

    def test_spatial_query(self):
        self.manifest.flush()
        for s in self.manifest.sources:
            s.search(self.geoj['geometry'])

        response = self.manifest.execute()
        self.assertEqual(list(response), self.valid_sources)

        expected_counts = [29, 10, 10, 20, 165, 1, 4]
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
                    self.assertEqual(feat['properties']['datetime'].split('-')[0], '2016')