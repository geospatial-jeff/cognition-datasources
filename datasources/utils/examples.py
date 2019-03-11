import json
import os
import click

from stac_validator.stac_validator import StacValidate

from datasources.sources import all, collections
from datasources import Manifest

# STAC doesn't work with vector (yet)
sources = list(set(all) - set(collections.vector))
example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../docs/examples/raster')

def build_examples():
    manifest = Manifest()
    manifest.load_sources(*sources)
    for source in manifest.sources:
        example = source.example()
        first_feature = example[source.__class__.__name__]['features'][0]
        with open(os.path.join(example_dir, '{}.json'.format(source.__class__.__name__)), 'w+') as outfile:
            json.dump(first_feature, outfile, indent=2)

def validate_examples():
    valids = []
    example_files = [os.path.join(example_dir, x) for x in os.listdir(example_dir)]
    for item in example_files:
        response = json.loads(StacValidate(item).run()[1:-1])
        if response['valid_stac']:
            valids.append(os.path.splitext(os.path.split(item)[-1])[0])
        else:
            print("INVALID!!", response)

    print("Valid datasources: {}".format(valids))