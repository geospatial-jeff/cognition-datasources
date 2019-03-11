# API Docs
The interface allows querying datasources with **spatial**, **temporal**, and **properties** parameters.  Spatial and temporal are standardized across all datasources while properties varies across datasources as different APIs have different responses.

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
The following table shows which STAC properties are available when querying each datasource with the `properties` parameter.  Metadata exposed by the API which doesn't fit into an existing STAC extension is given the `legacy` extension.  Currently, only **eo-epsg** and **eo-instrument** are available to all datasources, while **eo-gsd** is available to all except Sentinel1.  See the [datasource-reference](./datasource-reference.md) for more information.

| Name | STAC Properties | Legacy Properties | **kwargs |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|---------------------|
| ElevationTiles | [eo:gsd, eo:epsg, eo:instrument] | [legacy:x, legacy:y, legacy:z] | [limit, zoom] |
| CBERS | [eo:gsd: eo:epsg, eo:instrument, eo:platform, eo:sun_elevation, eo:sun_azimuth] | [legacy:path, legacy:row, legacy:processing_level] | [limit] |
| Landsat8 | [eo:gsd, eo:epsg, eo:instrument, eo:platform, eo:sun_elevation, eo:sun_azimuth, eo:off_nadir, eo:cloud_cover, eo:row, eo:column, landsat:processing_level] |  | [limit] |
| NAIP | [eo:gsd, eo:epsg, eo:instrument] |  |  |
| Sentinel1 | [eo:epsg, sar:polarization, sar:absolute_orbit, sar:type, sar:instrument_mode] | [legacy:lastorbitnumber, legacy:swathidentifier] | [limit] |
| Sentinel2 | [eo:gsd, eo:epsg, eo:instrument, eo:platform, eo:cloud_cover, eo:instrument, sentinel:utm_zone, sentinel:latitude_band, sentinel:grid_square, sentinel:sequence, sentinel:product_id] |  | [limit] |
| SRTM | [eo:gsd, eo:epsg, eo:instrument] | [legacy:x, legacy:y] | [limit] |
| USGS 3DEP | [eo:epsg, pc:count, pc:type, pc:encoding] | [legacy:scan] | [limit] |
| Microsoft Building Footprints | [eo:epsg] | [legacy:area, legacy:length, legacy:state] | [limit] |

### Response
The response is a dictionary of feature collections with a key for each searched datasource.  Each feature in the feature collection is a STAC Item representing a single asset returned by the query.  Example STAC Items for each datasource can be found [here](./examples).

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