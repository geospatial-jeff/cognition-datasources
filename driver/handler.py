from datasources import Manifest

def __TEMPLATENAME__(event, context):
    manifest = Manifest()
    manifest['__TEMPLATENAME__'].search(event['spatial'], event['temporal'], event['properties'], **event['kwargs'])
    response = manifest.execute()
    return response


