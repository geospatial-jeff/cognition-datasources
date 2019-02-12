import os
import subprocess
from multiprocessing.pool import ThreadPool
from osgeo import gdal, osr, ogr
from rtree import index

rtree_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'naip', 'naip_rtree')
naip_static_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'naip')

def download_manifest():
    subprocess.call("aws s3 cp s3://naip-analytic/manifest.txt {}/manifest.txt --request-payer requester".format(naip_static_location), shell=True)

def download_shapefile(key):
    subprocess.call("aws s3 sync s3://naip-analytic/{}/ {}/coverages/ --request-payer requester".format(key, naip_static_location), shell=True)

def download_coverages():
    keys = []
    with open(os.path.join(naip_static_location, 'manifest.txt'), 'r') as manifest:
        for line in manifest.readlines():
                line = line.rstrip()
                if line.endswith('.shp'):
                    keys.append(os.path.dirname(line))
    m = ThreadPool()
    m.map(download_shapefile, keys)

def build_database(shapefile=None):
    # Create transformer from NAD 83 to WGS 84
    in_srs = osr.SpatialReference()
    in_srs.ImportFromEPSG(4269)
    out_srs = osr.SpatialReference()
    out_srs.ImportFromEPSG(4326)
    transformer = osr.CoordinateTransformation(in_srs, out_srs)

    print("Preprocessing coverage shapefiles")
    # Preprocess into dict
    coverage_location = os.path.join(naip_static_location, 'coverages')
    files = [os.path.join(coverage_location, x) for x in os.listdir(coverage_location) if x.endswith('.shp')]
    d = {}
    for file in files:
        ds = gdal.OpenEx(file)
        if ds:
            lyr = ds.GetLayer()
            for feat in lyr:
                geom = feat.GetGeometryRef()
                if feat['Res'] == 0:
                    res = '60cm'
                else:
                    res = '100cm'
                state = os.path.splitext(file)[0].split('_')[-1]
                if feat['USGSID']:
                    key = "{}/{}/{}/rgbir/{}/{}".format(state,
                                                        feat['SrcImgDate'][:4],
                                                        res,
                                                        feat['USGSID'][:-2],
                                                        feat['FileName'])
                    # QKEY is unique id of each quad
                    if feat['QKEY'] not in d.keys():
                        # Reproject geometry to WGS 84
                        geom.Transform(transformer)
                        d[feat['QKEY']] = {'geometry': geom.ExportToWkt(), 'object': {'keys': [key], 'utm': 26900 + int(feat['UTM'])}}
                    else:
                        d[feat['QKEY']]['object']['keys'].append(key)
        else:
            print("Bad shapefile: {}".format(file))

    # Build index
    print("Building Rtree index")
    idx = index.Rtree(rtree_location)
    i = 0
    for quad in d:
        geometry = ogr.CreateGeometryFromWkt(d[quad]['geometry']).GetEnvelope()
        keys = d[quad]['object']
        idx.insert(i, (geometry[0], geometry[2], geometry[1], geometry[3]), obj=keys)
        i+=1

    # Create shapefile
    if shapefile:
        print("Creating shapefile")
        if type(shapefile) == str and shapefile.endswith('.shp'):
            out_ds = gdal.GetDriverByName('ESRI Shapefile').Create(shapefile,0,0,0)
            out_lyr = out_ds.CreateLayer('', out_srs, ogr.wkbPolygon)
            out_lyr.CreateField(ogr.FieldDefn("keys", ogr.OFTString))
            for quad in d:
                out_feat = ogr.Feature(out_lyr.GetLayerDefn())
                out_feat.SetField('keys', str(d[quad]['object']['keys']))
                geom = ogr.CreateGeometryFromWkt(d[quad]['geometry'])
                geom.Transform(transformer)
                out_feat.SetGeometry(geom)
                out_lyr.CreateFeature(out_feat)
                out_feat = None
            out_lyr = None
            out_ds = None