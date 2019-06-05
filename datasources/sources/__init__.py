

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

    CBERS = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-cbers"
    DGOpenData = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-dgopendata"
    ElevationTiles = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-elevationtiles"
    Landsat8 = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-landsat8"
    MicrosoftBuildingFootprints = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-mbf"
    NAIP = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-naip"
    PlanetData = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-planet"
    Sentinel1 = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-sentinel1"
    Sentinel2 = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-sentinel2"
    SRTM = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-srtm"
    USGS3DEP = "https://cdn.jsdelivr.net/gh/geospatial-jeff/cognition-datasources-usgs3dep"
