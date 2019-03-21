

class collections(object):

    def load_sources():
        import os
        source_files = os.listdir(os.path.dirname(__file__))
        sources = []
        for item in source_files:
            if item.endswith('.py') and item != '__init__.py' and item != 'base.py':
                module = os.path.splitext(item)[0]
                imported = getattr(__import__("datasources.sources.{}".format(module), fromlist=[module]), module)
                sources.append(imported)
        return sources

    all = load_sources()
    eo = [x for x in all if 'EO' in x.tags]
    ms = [x for x in all if 'MS' in x.tags]
    sar = [x for x in all if 'SAR' in x.tags]
    satellite = [x for x in all if 'Satellite' in x.tags]
    aerial = [x for x in all if 'Aerial' in x.tags]
    elevation = [x for x in all if 'Elevation' in x.tags]
    raster = [x for x in all if 'Raster' in x.tags]
    vector = [x for x in all if 'Vector' in x.tags]

class remote(object):

    Landsat8 = "https://raw.githubusercontent.com/geospatial-jeff/cognition-datasources-landsat8/master"
    Sentinel2 = "https://raw.githubusercontent.com/geospatial-jeff/cognition-datasources-sentinel2/master"
    NAIP = "https://raw.githubusercontent.com/geospatial-jeff/cognition-datasources-naip/master"
