import unittest

from datasources import Manifest


class BaseTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()

    def test_pattern(self):
        # Testing that datasource implements proper pattern
        for source in self.manifest.sources:
            self.assertTrue(hasattr(source, 'execute'))
            self.assertTrue(hasattr(source, 'search'))
            self.assertTrue(hasattr(source, 'tags'))
            self.assertTrue(hasattr(source, 'stac_compliant'))