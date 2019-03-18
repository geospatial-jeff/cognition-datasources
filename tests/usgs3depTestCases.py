import unittest
import geojson
from shapely.geometry import MultiPolygon, Polygon
from datasources import Manifest, sources

class USGS3DEPTestCases(unittest.TestCase):

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
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])
        self.temporal = ("2007-10-30", "2008-02-21")

    def test_3dep_pattern(self):
        self.assertEqual(hasattr(self.manifest['USGS3DEP'], 'execute'), True)
        self.assertEqual(hasattr(self.manifest['USGS3DEP'], 'search'), True)
        self.assertEqual(self.manifest['USGS3DEP'].stac_compliant, False)

    def test_3dep_search(self):
        self.manifest.flush()
        # Confirming that a simple search works internally
        self.manifest['USGS3DEP'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 4)

    def test_3dep_spatial_search(self):
        self.manifest.flush()
        self.manifest['USGS3DEP'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['USGS3DEP'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['USGS3DEP']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['USGS3DEP']['features']:
            mp = MultiPolygon([Polygon(x[0]) for x in feat['geometry']['coordinates']])
            self.assertTrue(mp.intersects(self.geoj_geom))

    def test_3dep_spatio_temporal_search(self):
        self.manifest.flush()

        self.manifest['USGS3DEP'].search(self.geoj['geometry'], temporal=self.temporal)
        response = self.manifest.execute()

        # Confirming dates of returned items are within temporal range (2017)
        for feat in response['USGS3DEP']['features']:
            acquisition_date = feat['properties']['datetime']
            self.assertEqual(acquisition_date.split('-')[0], self.temporal[0].split('-')[0])

    def test_3dep_spatio_temporal_properties_search(self):
        # Querying with pc:dataType
        self.manifest.flush()
        self.manifest['USGS3DEP'].search(self.geoj['geometry'], temporal=self.temporal, properties={'pc:encoding': {'eq': 'laszip'}})
        response = self.manifest.execute()
        [self.assertEqual(feat['properties']['pc:encoding'], 'laszip') for feat in response['USGS3DEP']['features']]

        # Querying with pc:count
        self.manifest.flush()
        self.manifest['USGS3DEP'].search(self.geoj['geometry'], temporal=self.temporal, properties={'pc:count': {'lt': 100000000}})
        response = self.manifest.execute()
        [self.assertTrue(feat['properties']['pc:encoding'] < 100000000) for feat in response['USGS3DEP']['features']]