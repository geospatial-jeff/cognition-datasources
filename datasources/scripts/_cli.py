import json
import click
import os
import requests
import tempfile
import time
import subprocess
import shutil
import yaml

from datasources import Manifest, sources
from datasources.utils.examples import build_examples, validate_examples


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
        md = yaml.load(r.text)
        build_info = requests.get(f'https://circleci.com/api/v1.1/project/github/{project_path}?circle-token={md["circle-token"]}&limit=1')
        build_status = build_info.json()[0]['status']
        if build_status != 'success':
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


@cognition_datasources.command(name='examples')
@click.option('--build/--no-build', default=False)
@click.option('--validate//no-validate', default=False)
def examples(build, validate):
    if build:
        build_examples()
    if validate:
        validate_examples()

@cognition_datasources.command(name="list")
def list():
    print([x.__name__ for x in sources.collections.all])




