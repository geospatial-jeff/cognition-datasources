import json

from datasources.sources import all, collections
from datasources import Manifest

# STAC doesn't work with vector (yet)
sources = list(set(all) - set(collections.vector))

def build_examples():
    manifest = Manifest()
    manifest.load_sources(*sources)
    responses = [x.example() for x in manifest.sources]
    for response in responses:
        datasource = list(response.keys())[0]
        feature_collection = response[datasource]
        first_feature = feature_collection['features'][0]
        with open('../../docs/examples/{}.json'.format(datasource), 'w+') as outfile:
            json.dump(first_feature, outfile, indent=2)


build_examples()
