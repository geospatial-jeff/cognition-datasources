
from datasources.stac.query import STACQuery
from datasources.sources.base import Datasource


class __TEMPLATENAME__(Datasource):

    stac_compliant = False
    tags = ['tag1', 'tag2']

    def __init__(self, manifest):
        super().__init__(manifest)

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        stac_query = STACQuery(spatial, temporal)

        api_request = #Parse stac_query into API-compatible JSON request, append to manifest

        self.manifest.searches.append([self, api_request])

    def execute(self, api_request):
        response = # api response

        if self.stac_compliant:
            # Return output as is (should be Feature Collection)
            return response
        else:
            # Parse api response into STAC-compliant item and return as list of STAC Items
            return [stac_item]