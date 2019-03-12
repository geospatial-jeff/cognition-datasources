from .landsat8 import Landsat8
from .naip import NAIP
from .sentinel1 import Sentinel1
from .sentinel2 import Sentinel2
from .srtm import SRTM
from .cbers import CBERS
from .elevationtiles import ElevationTiles
from .usgs3dep import USGS3DEP
from .dg_open_data import DGOpenData

from .microsoft_building_footprints import MicrosoftBuildingFootprints

all = [DGOpenData, Landsat8, NAIP, Sentinel1, Sentinel2, SRTM, CBERS, USGS3DEP, ElevationTiles, MicrosoftBuildingFootprints]

class collections(object):

    eo = [x for x in all if 'EO' in x.tags]
    ms = [x for x in all if 'MS' in x.tags]
    satellite = [x for x in all if 'Satellite' in x.tags]
    aerial = [x for x in all if 'Aerial' in x.tags]
    elevation = [x for x in all if 'Elevation' in x.tags]
    raster = [x for x in all if 'Raster' in x.tags]
    vector = [x for x in all if 'Vector' in x.tags]