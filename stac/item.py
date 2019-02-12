from schema import Schema, And
import re
import json

eo_extension = {
    'gsd': {'type': float},
    'platform': {'type': str},
    'constellation': {'type': str},
    'instrument': {'type': str},
    'bands': {'type': list},
    'epsg': {'type': int},
    'cloud_cover': {'type': float},
    'off_nadir': {'type': float},
    'azimuth': {'type': float},
    'sun_azimuth': {'type': float},
    'sun_elevation': {'type': float},
}

sar_extension = {
    'platform': {'type': str},
    'constellation': {'type': str},
    'instrument': {'type': str},
    'instrument_mode': {'type': str},
    'frequency_band': {'type': str},
    'center_wavelength': {'type': float},
    'center_frequency': {'type': float},
    'polarization': {'type': list},
    'bands': {'type': list},
    'pass_direction': {'type': str},
    'type': {'type': str},
    'resolution': {'type': float},
    'pixel_spacing': {'type': float},
    'looks': {'type': int},
    'absolute_orbit': {'type': list},
    'off_nadir': {'type': list},

}

class STACItemError(BaseException):
    pass

class STACItem(object):

    @staticmethod
    def validate_sar_extension(n):
        for (k,v) in n.items():
            if 'sar' in k:
                if type(v) != sar_extension[k.split(':')[-1]]['type']:
                    raise STACItemError("The {} property of the SAR extension is invalid.  Got {}, expecting {}.".format(k,
                                                                                                                         type(v),
                                                                                                                         sar_extension[k.split(':')[-1]]['type']))
        return True

    @staticmethod
    def validate_eo_extension(n):
        for (k,v) in n.items():
            if 'eo' in k:
                if type(v) != eo_extension[k.split(':')[-1]]['type']:
                    raise STACItemError("The {} property of the EO extension is invalid".format(k))
        return True

    @staticmethod
    def validate_assets(n):
        for (k,v) in n.items():
            if 'title' not in list(v) or 'href' not in list(v):
                raise STACItemError("STAC assets require 'title' and 'href'")
        return True

    @staticmethod
    def validate_bbox(n):
        # Expecting [xmin, ymin, xmax, ymax]
        valid = True
        if n[2] < n[0]:
            valid = False
            message = "Expected xmax is smaller than expected xmin"
        if n[3] < n[1]:
            valid = False
            message = "Expected ymax is smaller than expected ymin"
        if -180 > n[0] > 180 or -180 > n[2] > 180:
            valid = False
            message = "X values are outside of allowable range (-180, 180)"
        if -90 > n[0] > 90 or -90 > n[2] > 90:
            valid = False
            message = "Y values are outside of allowable range (-90, 90)"
        if valid:
            return valid
        else:
            raise STACItemError("STAC bbox error: {}".format(message))

    @staticmethod
    def validate_geometry(n):
        valid = True
        if 'type' not in list(n):
            valid = False
            message = "Geometry must contain `type` key"
        else:
            if n['type'] != 'Polygon':
                valid = False
                message = "Geometry must be of type `Polygon`"
        if 'coordinates' not in list(n):
            valid = False
            message = "Geometry must contain `coordinates` key"
        else:
            if type(n['coordinates']) != list:
                valid = False
                message = "Coordinates must be a list"
            else:
                if len(n['coordinates'][0][0]) != 2:
                    valid = False
                    message = "Coordinates should contain a nested list of depth 3"
        if valid:
            return valid
        else:
            raise STACItemError("STAC geometry error: {}".format(message))

    @classmethod
    def load(cls, stac_item):
        schema = Schema({
            "id": str,
            "type": And(
                str,
                'Feature'
            ),
            "properties": And(
                dict,
                # Confirming datetime is STAC compliant
                lambda n: re.match(r'^(19|20)\d\d-(0[1-9]|1[012])-([012]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d).(\d+?)Z$', n['datetime']),
                lambda n: cls.validate_eo_extension(n),
                lambda n: cls.validate_sar_extension(n)
            ),
            "assets": And(
                dict,
                lambda n: cls.validate_assets(n)
            ),
            "bbox": And(
                list,
                lambda n: cls.validate_bbox(n)
            ),
            "geometry": And(
                dict,
                lambda n: cls.validate_geometry(n)
            )
        })
        schema.validate(stac_item)
        return cls(stac_item)

    def __init__(self, stac_item):
        self.stac_item = stac_item

    @property
    def id(self):
        return self.stac_item['id']

    @property
    def type(self):
        return self.stac_item['type']

    @property
    def assets(self):
        return self.stac_item['assets']

    @property
    def bbox(self):
        return self.stac_item['bbox']

    @property
    def geometry(self):
        return self.stac_item['geometry']