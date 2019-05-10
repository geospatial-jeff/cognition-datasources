# API Docs

The [Spatio-Temporal-Asset-Catalog (STAC)](https://github.com/radiantearth/stac-spec) specification provides common metadata and API schemas to search and access geospatial data.  The standardized interface used by the library is based on the STAC spec and allows searching across three dimensions:

- **Spatial:** Find all assets which intersect a bounding box.
- **Temporal:** Find all assets acquired within a temporal window.
- **Properties:** Find all assets with certain  metadata.

Spatial is always required.  Temporal is always accepted but not always honored (not all spatial datasources are temporal).  Properties is always accepted but varies across drivers as different APIs have different responses.

### Spatial
The standard representation of space is a [GeoJSON geometry object](https://tools.ietf.org/html/rfc7946#section-3.1):

```json
{
 "type": "Polygon",
 "coordinates": [
  [
   [
    -118.95996093749999,
    34.95799531086792
   ],
   [
    -111.70898437499999,
    34.95799531086792
   ],
   [
    -111.70898437499999,
    40.74725696280421
   ],
   [
    -118.95996093749999,
    40.74725696280421
   ],
   [
    -118.95996093749999,
    34.95799531086792
   ]
  ]
 ]
}
```

### Temporal
The standard representation of time is tuple of strings indicating the start and end times of the query in UTC.  STAC requires dates to be formatted according to [RFC 3339 section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), as such the accepted formats are `YYYY-MM-DDTHH:mm:ss.msZ` and `YYYY-MM-DD`.

```python
date_notation = ("2018-10-30", "2018-12-31") # 2 months
date_time_notation = ("2018-10-30:T6:30:00.00Z", "2018-10-30:T8:30:00.00Z") # 2 hours
```

### Properties
The following table shows which STAC properties are available when querying each datasource with the `properties` parameter.  Metadata exposed by the API which doesn't fit into an existing STAC extension is given the `legacy` extension.  Currently, only **eo-epsg** is available to all datasources.  See the [datasource-reference](./datasource-reference.md) for more information.

| Name | STAC Properties | Legacy Properties | **kwargs |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|---------------------|
| Digital Globe Open Data | [eo:epsg] | [legacy:event_name, legacy:timeframe] | [limit] |
| ElevationTiles | [eo:gsd, eo:epsg, eo:instrument] | [legacy:x, legacy:y, legacy:z] | [limit, zoom] |
| CBERS | [eo:gsd: eo:epsg, eo:instrument, eo:platform, eo:sun_elevation, eo:sun_azimuth] | [legacy:path, legacy:row, legacy:processing_level] | [limit] |
| Landsat8 | [eo:gsd, eo:epsg, eo:instrument, eo:platform, eo:sun_elevation, eo:sun_azimuth, eo:off_nadir, eo:cloud_cover, eo:row, eo:column, landsat:processing_level] |  | [limit] |
| NAIP | [eo:gsd, eo:epsg, eo:instrument] |  |  |
| Sentinel1 | [eo:epsg, sar:polarization, sar:absolute_orbit, sar:type, sar:instrument_mode] | [legacy:lastorbitnumber, legacy:swathidentifier] | [limit] |
| Sentinel2 | [eo:gsd, eo:epsg, eo:instrument, eo:platform, eo:cloud_cover, eo:instrument, sentinel:utm_zone, sentinel:latitude_band, sentinel:grid_square, sentinel:sequence, sentinel:product_id] |  | [limit] |
| SRTM | [eo:gsd, eo:epsg, eo:instrument] | [legacy:x, legacy:y] | [limit] |
| USGS 3DEP | [eo:epsg, pc:count, pc:type, pc:encoding] | [legacy:scan] | [limit] |
| Microsoft Building Footprints | [eo:epsg] | [legacy:area, legacy:length, legacy:state] | [limit] |

Query strings are constructed using a nested dictionary notation.  For example, returning all items with a cloud cover of less than 5% looks like:

```
{'eo:cloud_cover: {'lt': 5}}
```

### Response
The response is a dictionary of feature collections with a key for each searched datasource.  Each feature in the feature collection is a STAC Item representing a single asset returned by the query.  Items returned from APIs which are not STAC compliant do not implement the standard `links` property, as there is no underlying STAC catalog to link with.  Example STAC Items for each datasource can be found in the [examples folder](./examples).

```json
{
  "Landsat8": {
    "type": "FeatureCollection",
    "features": [STACItem, STACItem, ... ]
  },
  "Sentinel2": {
    "type": "FeatureCollection",
    "features": [STACItem, STACItem, ... ]
  }
}
```

### Authentication
- Access to any datasources sourced by AWS Earth requires properly configured AWS credentials.  RequesterPay policies may apply.
- Access to Sentinel-1 requires a valid Copernicus Open Access Hub account with username and password saved to the `COPERNICUS_USER` and `COPERNICUS_PASSWORD` environment variables.

### Licencing and Data Rights
This library uses the [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/) which allows for commercial use but not all datasources exposed by the library are licensed for commercial use.  Please refer to the license of the underlying datasource before using commercially.

### Usage Examples
#### Cloud Deployment
```python
import requests
import json

endpoint = 'https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/stac/search'

payload = {
    'spatial': {'type:': 'Polygon': 'coordinates': [[...]]},
    'temporal': ("2018-10-30", "2018-12-31"),
    'properties': {'eo:cloud_cover': {'lte': 5}},
    'datasources': ['Landsat8', 'Sentinel2']
}

r = requests.post(endpoint, data=json.dumps(payload))
response = r.json()
```

#### Local Deployment
```python
from datasources import Manifest

payload = {
    'spatial': {'type:': 'Polygon': 'coordinates': [[...]]},
    'temporal': ("2018-10-30", "2018-12-31"),
    'properties': {'eo:cloud_cover': {'lte': 5}},
    'datasources': ['Landsat8', 'Sentinel2']
}

manifest = Manifest()
manifest['Landsat8'].search(**payload)
manifest['Sentinel2'].search(**payload)

response = manifest.execute()
```

Or with the CLI:

```
cognition-datasources search xmin ymin xmax ymax --start-date "2018-10-30" --end-date "2018-12-31" -d Landsat8 -d Sentinel2 --output response.json
```
