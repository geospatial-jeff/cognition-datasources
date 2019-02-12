import os
import json
from rtree import index

rtree_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasources', 'static', 'cbers', 'cbers_rtree')
data_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasources', 'static', 'cbers', 'cbers_reference.geojson')

def build_database():
    idx = index.Rtree(rtree_location)

    with open(data_location, 'r') as f:
        geoj = json.load(f)
        for i, feat in enumerate(geoj['features']):
            xcoords = [x[0] for x in feat['geometry']['coordinates'][0]]
            ycoords = [y[1] for y in feat['geometry']['coordinates'][0]]
            bbox = [min(xcoords), min(ycoords), max(xcoords), max(ycoords)]
            try:
                idx.insert(i,
                           bbox,
                           obj={
                               "row": feat['properties']['ROW'],
                               "path": feat['properties']['PATH'],
                               "geom": json.dumps(feat['geometry'])
                           })
            except TypeError:
                print(feat['geometry'])
                raise