import unittest

from datasources import Manifest
from shapely.geometry import Polygon


class BaseTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.name = self.__class__.__name__.replace('TestCases', '')
        self.manifest.update({self.name: self.datasource})
        self.spatial_geom = Polygon(self.spatial['coordinates'][0])

    def test_pattern(self):
        # Testing that datasource implements proper pattern
        for source in self.manifest.sources:
            self.assertTrue(hasattr(source, 'execute'))
            self.assertTrue(hasattr(source, 'search'))
            self.assertTrue(hasattr(source, 'tags'))
            self.assertTrue(hasattr(source, 'stac_compliant'))

    def test_spatial_search(self):
        self.manifest.flush()
        self.manifest[self.name].search(self.spatial)
        response = self.manifest.execute()

        # Confirming that each outptu featuer intersects input
        for feat in response[self.name]['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertTrue(asset_geom.intersects(self.spatial_geom))