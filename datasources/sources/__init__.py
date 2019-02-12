from .landsat8 import Landsat8
from .naip import NAIP
from .sentinel1 import Sentinel1
from .sentinel2 import Sentinel2
from .srtm import SRTM
from .cbers import CBERS
from .elevationtiles import ElevationTiles

all = [Landsat8, NAIP, Sentinel1, Sentinel2, SRTM, CBERS, ElevationTiles]
