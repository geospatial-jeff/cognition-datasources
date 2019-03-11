import unittest
import geojson
from shapely.geometry import Polygon
from datasources import Manifest, sources


class MicrosoftBuildingFootprintTestCases(unittest.TestCase):

    def setUp(self):
        self.manifest = Manifest()
        self.manifest.load_source("MicrosoftBuildingFootprints")
        self.geoj = {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                          -118.31877350807191,
                          34.07821170392112
                        ],
                        [
                          -118.31773281097412,
                          34.07821170392112
                        ],
                        [
                          -118.31773281097412,
                          34.07897593175943
                        ],
                        [
                          -118.31877350807191,
                          34.07897593175943
                        ],
                        [
                          -118.31877350807191,
                          34.07821170392112
                        ]
                      ]
                    ]
                  }
                }
        self.geoj_geom = Polygon(self.geoj['geometry']['coordinates'][0])

    def test_manifest_load(self):
        self.assertEqual(list(self.manifest), ['MicrosoftBuildingFootprints'])
        self.assertEqual(type(self.manifest['MicrosoftBuildingFootprints']), sources.MicrosoftBuildingFootprints)

    def test_msbf_search(self):
        self.manifest.flush()

        # Confirming that a simple search works internally
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'])
        self.assertEqual(len(self.manifest.searches), 1)
        self.assertEqual(type(self.manifest.searches[0][0]), sources.MicrosoftBuildingFootprints)

    def test_msbf_spatial_search(self):
        self.manifest.flush()
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'])
        response = self.manifest.execute()
        self.assertEqual(list(response), ['MicrosoftBuildingFootprints'])

        # Confirming output is a valid feature collection
        feature_collection = geojson.FeatureCollection([geojson.Feature(feat) for feat in response['MicrosoftBuildingFootprints']['features']])
        self.assertEqual(len(feature_collection.errors()), 0)

        # Confirming that each output feature intersects the input
        for feat in response['MicrosoftBuildingFootprints']['features']:
            asset_geom = Polygon(feat['geometry']['coordinates'][0])
            self.assertTrue(asset_geom.intersects(self.geoj_geom))

    def test_msbf_spatial_properties_search(self):
        self.manifest.flush()
        # Querying with legacy:area
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'], properties={'legacy:area': {'lt': 60}})
        response = self.manifest.execute()
        [self.assertTrue(x['properties']['legacy:area']<60) for x in response['MicrosoftBuildingFootprints']['features']]


        self.manifest.flush()
        # Querying with legacy:length
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'], properties={'legacy:area': {'gt': 30}})
        response = self.manifest.execute()
        [self.assertTrue(x['properties']['legacy:area']>30) for x in response['MicrosoftBuildingFootprints']['features']]

        self.manifest.flush()
        # Querying with eo:epsg (changes the spatial reference of returned features)
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'], properties={'eo:epsg': {'eq': 32611}})
        response = self.manifest.execute()
        [self.assertEqual(x['properties']['eo:epsg'], 32611) for x in response['MicrosoftBuildingFootprints']['features']]

    def test_msbf_limit(self):
        """
        The limit kwarg changes the default behavior of the API.  The underlying ESRI Feature Layer returns a limit of
        2000 feature sets from a single GET request.  Returning more than 2000 feature sets requires 2 GET requests, the first
        using the `returnIdsOnly` API keyword which returns a list of object IDs, the second using the `objectIds` API
        keyword to return each feature set.
        """
        # The search area contains 19 geometries, test for equality with both behaviors
        self.manifest.flush()
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'], limit=3000)
        response1 = self.manifest.execute()

        self.manifest.flush()
        self.manifest['MicrosoftBuildingFootprints'].search(self.geoj['geometry'], limit=1000)
        response2 = self.manifest.execute()

        self.assertEqual(len(response1['MicrosoftBuildingFootprints']['features']), len(response2['MicrosoftBuildingFootprints']['features']))




