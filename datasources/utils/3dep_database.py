import os
import json
from multiprocessing.pool import ThreadPool
import boto3

from rtree import index


rtree_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', '3dep', '3dep_rtree')
bucket = 'usgs-lidar-public'

client = boto3.client('s3')


def project_names():
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/'):
        for prefix in result.get('CommonPrefixes'):
            yield prefix.get('Prefix')

def project_info(project_name):
    splits = project_name.split('_')
    if splits[0] == 'USGS':
        try:
            year = int(splits[-3])
        except:
            year = int(splits[-1][:-1])
    else:
        try:
            year = int(splits[-1][:-1])
        except:
            year = None

    try:
        response = client.get_object(Bucket=bucket, Key=os.path.join(project_name, 'boundary.json'))
        json_content = response['Body'].read().decode('utf-8')
        return {'year': year, 'geojson': json.loads(json_content), 'name': project_name[:-1]}
    except:
        print("WARNING!! No geometry found for the {} project".format(project_name))
        return None

def build_database():
    idx = index.Rtree(rtree_location)

    m = ThreadPool()
    responses = [x for x in m.map(project_info, project_names()) if x]
    i = 0
    for resp in responses:
        for geom in resp['geojson']['coordinates']:
            xcoords = [x[0] for x in geom[0]]
            ycoords = [y[1] for y in geom[0]]
            bbox = [min(xcoords), min(ycoords), max(xcoords), max(ycoords)]
            idx.insert(i,
                       bbox,
                       obj = {
                           "year": resp['year'],
                           "project_name": resp['name'],
                           "geom": json.dumps(resp['geojson'])
                       })

# build_database()
