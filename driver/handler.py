from datasources import Manifest

def handler(event, context):
    manifest = Manifest()
    manifest['__TEMPLATENAME__'].search(event['spatial'], event['temporal'], event['properties'], **event['kwargs'])
    response = manifest.execute()
    return response


