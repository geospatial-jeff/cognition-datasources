import json
import click
import os
import requests
import tempfile
import time
import subprocess
import shutil
import yaml
from multiprocessing.pool import ThreadPool

from datasources import Manifest, sources

@click.group(short_help="Cognition datasource query")
def cognition_datasources():
    pass

@cognition_datasources.command(name="search")
@click.option('--spatial', type=float, nargs=4, required=True)
@click.option('--start_date', '-sd', type=str, help="Start date as either YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss:%fZ")
@click.option('--end_date', '-ed', type=str, help="End date as either YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss:%fZ")
@click.option('--properties', '-p', type=str, help="STAC properties for filtering query results")
@click.option('--datasource', '-d', type=str, multiple=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--output', '-o', type=click.File(mode='w'))
def search(spatial, start_date, end_date, properties, datasource, debug, output):
    if debug:
        start = time.time()

    geoj = {
        "type": "Polygon",
        "coordinates": [
            [
                [spatial[0], spatial[3]],
                [spatial[2], spatial[3]],
                [spatial[2], spatial[1]],
                [spatial[0], spatial[1]],
                [spatial[0], spatial[3]]
            ]
        ]
    }

    temporal = (start_date, end_date) if start_date and end_date else None

    manifest = Manifest()
    for source in datasource:
        manifest.load_source(getattr(sources, source))
        manifest[source].search(geoj, temporal=temporal, properties=properties, limit=10)

    if debug:
        click.echo("Number of searches: {}".format(len(manifest.searches)))

    response = manifest.execute()

    if debug:
        for item in list(response):
            print("Found {} features for {}".format(len(response[item]['features']), item))

    if output:
        json.dump(response, output)

    if debug:
        print("Runtime: {}".format(time.time()-start))

    return 0


@cognition_datasources.command(name='new')
@click.option('--name', '-n', type=str)
def new(name):
    if os.path.exists(name):
        raise ValueError("The directory {} already exists.".format(name))

    shutil.copytree(os.path.join(os.path.dirname(__file__), '..', 'template'), name)

    with open(os.path.join(os.getcwd(), name, 'template.py'), 'r') as f:
        contents = f.read()
        contents = contents.replace('__TEMPLATENAME__', name)

        with open(os.path.join(os.getcwd(), name, 'template.py'), 'w') as outf:
            outf.write(contents)

    with open(os.path.join(os.getcwd(), name, 'tests.py'), 'r') as f:
        contents = f.read()
        contents = contents.replace('__TEMPLATENAME__', name)

        with open(os.path.join(os.getcwd(), name, 'tests.py'), 'w') as outf:
            outf.write(contents)

    os.rename(os.path.join(os.getcwd(), name, 'template.py'), os.path.join(os.getcwd(), name, '{}.py'.format(name)))


@cognition_datasources.command(name='load')
@click.option('--datasource', '-d', type=str, multiple=True)
def load(datasource):
    for source in datasource:
        source_link = getattr(sources.remote, source)
        project_path = '/'.join(source_link.split('/')[3:-1])

        # Check CI build
        r = requests.get(os.path.join(source_link, 'config.yml'))
        md = yaml.load(r.text, Loader=yaml.BaseLoader)
        build_info = requests.get(f'https://circleci.com/api/v1.1/project/github/{project_path}?circle-token={md["circle-token"]}&limit=1')
        build_status = build_info.json()[0]['status']
        if build_status != 'success':
            print("WARNING: {} was not loaded because it failed CI".format(source))
            continue

        # Download remote datasource .py file into sources folder
        source_fname = source + '.py'
        source_remote_url = os.path.join(source_link, source_fname)
        r = requests.get(source_remote_url)
        with open(os.path.join(os.path.dirname(__file__), '..', 'sources', source_fname), 'w+') as outfile:
            outfile.write(r.text)

        # Install datasource dependencies
        fd, path = tempfile.mkstemp()
        req_remote_url = os.path.join(source_link, 'requirements.txt')
        try:
            with os.fdopen(fd, 'w') as tmp:
                r = requests.get(req_remote_url)
                tmp.write(r.text)
        finally:
            subprocess.call("pip install -r {}".format(path), shell=True)
            os.remove(path)

        # Check for index
        idx_remote_url = os.path.join(source_link, 'index.idx')
        dat_remote_url = os.path.join(source_link, 'index.dat')

        idx_r = requests.get(idx_remote_url)
        dat_r = requests.get(dat_remote_url)

        if idx_r.status_code == 404 or dat_r.status_code == 404:
            continue

        with open(os.path.join(os.path.dirname(__file__), '..', 'static', '{}_rtree.idx'.format(source)), 'wb+') as outfile:
            outfile.write(idx_r.content)

        with open(os.path.join(os.path.dirname(__file__), '..', 'static', '{}_rtree.dat'.format(source)), 'wb+') as outfile:
            outfile.write(dat_r.content)

@cognition_datasources.command(name='build-examples')
def build_examples():
    from datasources.sources import remote
    remote_assets = {k: v for (k, v) in remote.__dict__.items() if type(v) == str and 'https' in v}
    example_rel_path = 'docs/example.json'

    def _fetch_examples(data):
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'examples', '{}.json'.format(data['name'])),
                  'wb+') as examplefile:
            r = requests.get(os.path.join(data['url'], example_rel_path))
            examplefile.write(r.content)

    m = ThreadPool()
    m.map(_fetch_examples, [{'name': k, 'url': v} for k,v in remote_assets.items()])

@cognition_datasources.command(name='build-docs')
def build_docs():
    from datasources.sources import remote
    remote_assets = {k: v for (k, v) in remote.__dict__.items() if type(v) == str and 'https' in v}
    docs_rel_path = 'docs/README.md'

    def _fetch_docs(data):
        r = requests.get(os.path.join(data['url'], docs_rel_path))
        return {data['name']: r.content}

    m = ThreadPool()
    response = m.map(_fetch_docs, [{'name': k, 'url': v} for k,v in remote_assets.items()])
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'datasource-reference_v2.md'), 'wb+') as docfile:
        for item in response:
            name = list(item.keys())[0]
            md = item[name]

            docfile.write(md)
            docfile.write(b"\n---\n")


