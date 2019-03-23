
class Datasource(object):

    stac_compliant = False
    tags = ['tag1', 'tag2']

    def __init__(self, manifest):
        self.manifest = manifest

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        """
        Method to preprocess spatial/temporal/properties arguments into arguments compatible with specific API.
        """
        raise NotImplementedError

    def execute(self, query):
        """
        Method to execute API request using arguments generated with `search` method and return as STAC item.
        """
        pass

    def execute_multi(self, query_body, conn):
        """Internal use"""
        response = self.execute(query_body)
        conn.send({'stac_items': response, 'source': self.__class__.__name__})
        conn.close()

