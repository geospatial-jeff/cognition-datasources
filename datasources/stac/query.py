import operator
from datetime import datetime
import os

from schema import Schema, And
from geomet import wkt


class STACQueryError(BaseException):
    pass

class STACQuery(object):

    @staticmethod
    def load_spatial(spatial):
        schema = Schema({
            "type": And(
                str,
                lambda n: n == "Polygon"
            ),
            "coordinates": And(
                # Checking type of coordinates
                list,
                # Confirming the geometry is closed (the first and last positions are equivalent)
                lambda n: n[0][0] == n[0][-1],
                # Confirming individual coordinates are [lat, long] ordered
                lambda n: len(list(filter(lambda x: -180 <= x[0] <= 180, n[0]))) == len(n[0]),
                lambda n: len(list(filter(lambda y: -90 <= y[1] <= 90, n[0]))) == len(n[0])
        )
        })
        schema.validate(spatial)
        return spatial

    @staticmethod
    def load_temporal(temporal):
        type_schema = Schema((str, str))
        type_schema.validate(temporal)

        # Validate the dates individually
        for idx, item in enumerate(temporal):
            # Checking for full-date notation "YYYY-MM-DD"
            if len(item) == 10:
                date_schema = Schema(
                    And(
                        lambda n: 0 <= int(n.split('-')[0]) <= 2100,
                        lambda n: 1 <= int(n.split('-')[1]) <= 12,
                        lambda n: 1 <= int(n.split('-')[2]) <= 31,
                        error="Invalid configuration, must be of format `YYYY-MM-DD`"
                    )
                )
                date_schema.validate(item)
                _date = datetime.strptime("{}T00:00:00.000Z".format(item), "%Y-%m-%dT%H:%M:%S.%fZ")
            # Checking for full-date-full-time notation "YYYY-MM-DDT:hh:mm:ss.msZ"
            elif len(item) == 24:
                date_schema = Schema(
                    And(
                        lambda n: 0 <= int(n.split('-')[0]) <= 2100, # YYYY
                        lambda n: 1 <= int(n.split('-')[1]) <= 12, # MM
                        lambda n: 1 <= int(n.split('-')[2].split('T')[0]) <= 31, # DD
                        lambda n: n[10] == 'T',
                        lambda n: 0 <= int(n.split(':')[0].split('T')[-1]) <= 24, # hh
                        lambda n: 0 <= int(n.split(':')[1]) <= 60, # mm
                        lambda n: 0 <= int(n.split(':')[-1].split('.')[0]) <= 60, # ss
                        lambda n: 0 <= int(n.split(':')[-1].split('.')[-1][:-1]) <= 999, # ms
                        lambda n: n[-1] == 'Z',
                        error="Invalid temporal configuration, must be of format `YYYY-MM-DDThh:mm:ss.mssZ`"
                    )
                )
                date_schema.validate(item)
                _date = datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                raise STACQueryError("Temporal must be of form `YYYY-MM-DD` or `YYYY-MM-DDThh:mm:ss.msZ`")


            if idx == 0:
                start_date = _date
            elif idx == 1:
                end_date = _date

        if start_date > end_date:
            raise STACQueryError("Temporal must be of form (start_date, end_date)")

        return (start_date, end_date)



    def __init__(self, spatial, temporal=None, properties=None):
        self.spatial = self.load_spatial(spatial)
        if temporal:
            self.temporal = self.load_temporal(temporal)
        if properties:
            self.properties = properties


    def bbox(self):
        """
        :return: Standard STAC bounding box of [xmin, ymin, xmax, ymax]
        """
        return [
            min([x[0] for x in self.spatial['coordinates'][0]]),
            min([x[1] for x in self.spatial['coordinates'][0]]),
            max([x[0] for x in self.spatial['coordinates'][0]]),
            max([x[1] for x in self.spatial['coordinates'][0]]),
        ]

    def wkt(self):
        return wkt.dumps(self.spatial)

    def check_temporal(self, date_time):
        if self.temporal[0] <= date_time <= self.temporal[1]:
            return True
        else:
            return False

    def check_properties(self, asset):
        for item in self.properties:
            equality = next(iter(self.properties[item]))
            comparison_operator = getattr(operator, equality)
            if not comparison_operator(asset[item], self.properties[item][equality]):
                return False
        return True

    # def check_spatial(self, name):
    #     static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    #     rtree_location = os.path.join(static_dir, '{}_rtree'.format(name))
    #
    #     try:
    #         idx = index.Rtree(rtree_location)
    #         return [x.object for x in idx.intersection(self.bbox(), objects=True)]
    #     except:
    #         # Look for rtree in current directory
    #         try:
    #             idx = index.Rtree('index')
    #             return [x.object for x in idx.intersection(self.bbox(), objects=True)]
    #         except:
    #             raise FileNotFoundError("Could not find rtree for the datasource at the following path: {}".format(rtree_location))
