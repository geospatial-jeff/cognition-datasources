from datasources import Manifest

def __TEMPLATENAME__(event, context):
    manifest = Manifest()
    manifest['__TEMPLATENAME__'].search(**event)
    response = manifest.execute()
    return response


