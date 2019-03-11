from multiprocessing import Process, Pipe

from datasources import sources

class Manifest(dict):

    def __init__(self):
        super().__init__()
        self.searches = []

    @property
    def sources(self):
        for (k,v) in self.items():
            yield v

    def load_source(self, source):
        if type(source) == str:
            self.update({source: getattr(sources, source)(self)})
        else:
            self.update({source.__name__: source(self)})

    def load_sources(self, *args):
        list(map(lambda n: self.load_source(n), args))

    def flush(self):
        self.searches = []

    def execute(self):
        response = {}
        for search in self.searches:
            source_name = search[0].__class__.__name__
            if source_name not in response:
                response.update({source_name: {
                    "type": "FeatureCollection",
                    "features": []
                }})

        # Execute searches (lambda safe)
        processes = []
        parent_connections = []

        # print("Creating processes")
        for search in self.searches:
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)
            process = Process(target=search[0].execute_multi, args=(search[1], child_conn))
            processes.append(process)

        # print("Starting processes")
        for process in processes:
            process.start()

        # print("Joining processes")
        for process in processes:
            process.join()


        for parent_connection in parent_connections:
            resp = parent_connection.recv()
            if resp['stac_items']:
                stac_compliant = getattr(sources, resp['source']).stac_compliant
                if stac_compliant:
                    response.update({resp['source']: resp['stac_items']})
                else:
                    [response[resp['source']]['features'].append(x) for x in resp['stac_items']]

        return response