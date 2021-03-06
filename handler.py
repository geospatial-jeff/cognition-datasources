import os
from multiprocessing import Process, Pipe
import json

from datasources import Manifest
import boto3

service = os.environ['SERVICE_NAME']
stage = os.environ['SERVICE_STAGE']
region = os.environ['SERVICE_REGION']

lambda_client = boto3.client('lambda')

def worker(event, context):

    def lambda_invoke(service, stage, source, args, conn=None, multi=False):
        response = lambda_client.invoke(
            FunctionName=f"{service}-{stage}-{source}",
            InvocationType="RequestResponse",
            Payload=json.dumps(args)
        )
        data = json.loads(response['Payload'].read())
        if multi:
            conn.send(data)
            conn.close()
        else:
            return data

    package = json.loads(event['body'])
    params = list(package)
    args = {}
    out_d = {}

    if 'time' in params:
        args.update({'temporal': package['time'].split('/')})
    else:
        args.update({'temporal': None})

    if 'intersects' in params:
        args.update({'spatial': package['intersects']})
    elif 'bbox' in params:
        geoj = {
            "type": "Polygon",
            "coordinates": [
                [
                    [package['bbox'][0], package['bbox'][3]],
                    [package['bbox'][2], package['bbox'][3]],
                    [package['bbox'][2], package['bbox'][1]],
                    [package['bbox'][0], package['bbox'][1]],
                    [package['bbox'][0], package['bbox'][3]]
                ]
            ]
        }
        args.update({'spatial': geoj})
    else:
        raise ValueError("Spatial parameter is required")

    if 'properties' in params:
        args.update({'properties': package['properties']})
    else:
        args.update({'properties': None})

    if 'limit' in params:
        args.update({'limit': package['limit']})
    else:
        args.update({'limit': 10})

    if 'subdatasets' in params:
        args.update({'subdatasets': package['subdatasets']})

    processes = []
    parent_connections = []

    if len(package['datasources']) == 1:
        source = list(package['datasources'])[0]
        return {
            'statusCode': 200,
            'body': json.dumps(lambda_invoke(service, stage, source, args, multi=False))
        }

    for source in package['datasources']:
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)

        process = Process(target=lambda_invoke, args=(service, stage, source, args, child_conn, True))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    for parent_connection in parent_connections:
        response = parent_connection.recv()
        for item in response:
            if item not in list(out_d):
                out_d.update({item: response[item]})
            else:
                out_d[item]['features'] += response[item]['features']

    return {
        'statusCode': 200,
        'body': json.dumps(out_d)
    }

