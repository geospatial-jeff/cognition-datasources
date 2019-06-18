from multiprocessing import Process, Pipe

from datasources.sources import collections

class Manifest(dict):

    # shouldn't use mutable default
    def __init__(self, tags=['all']):
        super().__init__()
        self.searches = []
        self.load_sources(tags)

    @property
    def sources(self):
        for (k,v) in self.items():
            yield v

    def load_sources(self, tags):
        tagged = []
        for tag in tags:
            tagged += getattr(collections, tag)
        tagged = list(set(tagged))

        for source in tagged:
            self.update({source.__name__: source(self)})


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

        response_list = []
        # Run in main process if only a single search
        if len(self.searches) == 1:
            print("Detecting a single search (inside driver)")
            resp = {
                'stac_items': self.searches[0][0].execute(self.searches[0][1]),
                'source': self.searches[0][0].__class__.__name__
            }
            print(resp)
            response_list.append(resp)
        # Spawn child processes if multiple searches
        else:
            processes = []
            parent_connections = []

            for search in self.searches:
                parent_conn, child_conn = Pipe()
                parent_connections.append(parent_conn)
                process = Process(target=search[0].execute_multi, args=(search[1], child_conn))
                processes.append(process)

            for process in processes:
                process.start()

            for process in processes:
                process.join()

            for parent_connection in parent_connections:
                resp = parent_connection.recv()
                response_list.append(resp)

        # Format driver response into feature collection
        for resp in response_list:
            if resp['stac_items']:
                stac_compliant = self[resp['source']].stac_compliant
                if stac_compliant:
                    response.update({resp['source']: resp['stac_items']})
                else:
                    [response[resp['source']]['features'].append(x) for x in resp['stac_items']]

        return response