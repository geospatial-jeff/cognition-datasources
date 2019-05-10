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

from datasources import Manifest, sources, layer_arn

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

    shutil.copytree(os.path.join(os.path.dirname(__file__), '..', '..', 'driver'), name)

    fpaths = [
        os.path.join(os.getcwd(), name, 'template.py'),
        os.path.join(os.getcwd(), name, 'tests.py'),
        os.path.join(os.getcwd(), name, 'bin', 'driver-package.sh'),
        os.path.join(os.getcwd(), name, 'handler.py'),
        os.path.join(os.getcwd(), name, 'README.md')
    ]

    for file in fpaths:
        replace_template_name(file, name)

    os.rename(fpaths[0], os.path.join(os.path.dirname(fpaths[0]), f'{name}.py'))

@cognition_datasources.command(name='load')
@click.option('--datasource', '-d', type=str, multiple=True)
@click.option('--local/--deployed', default=False)
def load(datasource, local):

    handler = []
    sls_functions = {}

    for source in datasource:
        print("Loading the {} driver.".format(source))
        source_link = getattr(sources.remote, source)
        project_path = '/'.join(source_link.split('/')[4:])
        source_link += '@master'

        # Check CI build
        r = requests.get(os.path.join(source_link, 'config.yml'))
        md = yaml.load(r.text, Loader=yaml.BaseLoader)
        build_info = requests.get(f'https://circleci.com/api/v1.1/project/github/{project_path}?circle-token={md["circle-token"]}&limit=1')
        build_status = build_info.json()[0]['status']
        if build_status != 'success':
            print("WARNING: {} was not loaded because it failed CI".format(source))
            continue

        # Download remote file handler
        handler_url = os.path.join(source_link, 'handler.py')
        r = requests.get(handler_url)
        for line in r.text.splitlines()[2:]:
            handler.append(line + '\n')

        # Build sls function config
        sls_functions.update({
            source: {
                'handler': 'handler.' + source,
                'layers': [
                    layer_arn,
                    md['layer-arn'],
                ]
            }
        })

        # Add database layer arn if present
        if 'db-arn' in md:
            sls_functions[source]['layers'].append(md['db-arn'])


        if local:
            # Download driver file to local installation of cognition-datasources
            driver_url = os.path.join(source_link, f"{source}.py")
            r = requests.get(driver_url)
            with open(os.path.join(os.path.dirname(__file__), '..', 'sources', f"{source}.py"), "w+") as driver_file:
                driver_file.write(r.text)

            # Install dependencies
            fd, path = tempfile.mkstemp()
            req_url = os.path.join(source_link, "requirements.txt")
            try:
                with os.fdopen(fd, 'w') as tmp:
                    r = requests.get(req_url)
                    tmp.write(r.text)
            finally:
                subprocess.call("pip install -r {}".format(path), shell=True)
                os.remove(path)

    # Write handler.py
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'handler.py'), 'a+') as outfile:
        for line in handler:
            outfile.write(line)

    # Write serverless.yml
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'serverless.yml'), 'r+') as config:
        contents = yaml.load(config, Loader=yaml.BaseLoader)
        contents['functions'].update(sls_functions)

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'serverless.yml'), 'w+') as outfile:
            yaml.dump(contents, outfile)


@cognition_datasources.command(name='build-examples')
def build_examples():
    from datasources.sources import remote
    remote_assets = {k: v for (k, v) in remote.__dict__.items() if type(v) == str and 'https' in v}
    example_rel_path = 'docs/example.json'

    def _fetch_examples(data):
        print("Pulling example for {}.".format(data['name']))
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
    docs_rel_path = 'README.md'

    build_status = []
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'datasource-reference.md'), 'wb+') as docfile:
        for item in remote_assets:
            print("Pulling docs for {}.".format(item))
            r = requests.get(os.path.join(remote_assets[item], docs_rel_path))
            docfile.write(r.content)
            docfile.write(b"\n---\n")

            lines = r.text.splitlines()
            if 'CircleCI' in lines[0]:
                build_status.append({'name': item, 'status': lines[0]})

    print("Finishing up.")
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'datasource-status.md'), 'w+') as statusfile:
        statusfile.write("# Driver Status\n")
        statusfile.write("| Driver Name | Status |\n")
        statusfile.write("| ----- | ----- |\n")
        for item in build_status:
            statusfile.write("| {} | {} |\n".format(item['name'], item['status']))


@cognition_datasources.command(name='list')
def list():
    from datasources.sources import collections
    sources = collections.load_sources()
    print([x.__name__ for x in sources])


# Some helper methods used by the CLI
def replace_template_name(fpath, name):
    with open(fpath, 'r') as f:
        contents = f.read()
        contents = contents.replace('__TEMPLATENAME__', name)

        with open(fpath, 'w') as outf:
            outf.write(contents)