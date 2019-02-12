
class Datasource(object):

    def __init__(self, manifest):
        self.stac_compliant = False
        self.manifest = manifest

    def search(self, spatial, temporal, properties):
        """
        Method to preprocess spatial/temporal/properties arguments into arguments compatible with specific API with
        help of `load_spatial`, `load_temporal`, and `load_kwargs`
        """
        raise NotImplementedError

    def execute(self, query_body):
        """
        Method to execute API request using arguments generated with `search` method
        """
        pass

    def execute_multi(self, query_body, conn):
        response = self.execute(query_body)
        conn.send({'stac_item': response, 'source': self.__class__.__name__})
        conn.close()

    def load_spatial(self, spatial, bbox=False):
        """
        Method to load STAC spatial argument as API compatible argument
        """
        raise NotImplementedError

    def load_temporal(self, temporal):
        """
        Method to load STAC temoral argument as API compatible argument
        """
        raise NotImplementedError

    def load_kwargs(self, kwargs):
        """
        Method to load STAC kwargs argument as API compatible argument
        """
        raise NotImplementedError