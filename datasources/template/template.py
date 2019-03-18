
from datasources.stac.query import STACQuery
from datasources.sources.base import Datasource


class __TEMPLATENAME__(Datasource):

    stac_compliant = True
    tags = ['tag1', 'tag2']

    def __init__(self, manifest):
        super().__init__(manifest)

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        stac_query = STACQuery(spatial, temporal)
        pass


    def execute(self, query):
        pass