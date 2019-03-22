## CBERS

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 20.0 |
| eo:epsg | int | 32614 |
| eo:instrument | str | 'AWFI' |
| eo:platform | str | 'CBERS' |
| eo:sun_azimuth | float | 154.88 |
| eo:sun_elevation | float | 28.26 |
| legacy:row | str | '230' |
| legacy:path | str | '049' |
| legacy:processing_level | str | 'L2' |
---
## DG Open Data

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:epsg | int | 4326 |
| legacy:event_name | str | 'california-wildfires' |
| legacy:timeframe | str | 'post-event' |

##### Notes
- There is no source API for this datasource, instead an index is created with the [dg-open-data-scraper](https://github.com/geospatial-jeff/dg-open-data-scraper).
---
## Elevation Tiles

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :x: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit, zoom] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 305.74 |
| eo:epsg | int | 3857 |
| eo:instrument | str | 'srtm' |
| legacy:x| int | 55 |
| legacy:y | int | 91 |
| legacy:z | int | 8 |

##### Notes
- The source API is a XYZ tiled elevation service.  The `zoom` kwarg changes the zoom level being queried.
- The source API doesn't support temporal data.  Can search with temporal but it is not honored.
---
## Landsat8

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 20.0 |
| eo:epsg | int | 32614 |
| eo:instrument | str | 'OLI_TIRS' |
| eo:platform | str | 'landsat-8' |
| eo:sun_azimuth | float | 154.88 |
| eo:sun_elevation | float | 28.26 |
| eo:off_nadir | float | 1.0 |
| eo:cloud_cover | float | 1.0 |
| eo:row | str | '030' |
| eo:column | str | '032' |
| landsat:processing_level | str | 'L1TP' |
---
## Microsoft Building Footprints

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :x: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:epsg | int | 3857 |
| legacy:x | str | 'W102' |
| legacy:area | float | 100.0 |
| legacy:length | float | 30.0 |
| legacy:state | str | 'CA' |


##### Notes
- The source API doesn't support temporal data.  Can search with temporal but it is not honored.
---
## NAIP

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 1.0 |
| eo:epsg | int | 26914 |
| eo:instrument | str | 'Leica ADS100' |
---
## SRTM

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :x: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 305.74 |
| eo:epsg | int | 3857 |
| eo:instrument | str | 'srtm' |
| legacy:x | str | 'W102' |
| legacy:y | str | 'N44' |
---
## Sentinel1

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:epsg | int | 32614 |
| sar:polarization | list | ['VV', 'VH'] |
| sar:absolute_orbit | int | 25101 |
| sar:type | str | 'SLC' |
| sar:instrument_mode | str | 'IW' |
| legacy:lastorbitnumber | int | 14760 |
| legacy:swathidentifier | str | 'IW1 IW2 IW3' |
---
## Sentinel2

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 10.0 |
| eo:epsg | int | 32614 |
| eo:instrument | str | 'MSI' |
| eo:platform | str | 'sentinel-2b' |
| eo:off_nadir | float | 0.0 |
| eo:cloud_cover | float | 100.0 |
| sentinel:utm_zone | int | 13 |
| sentinel:latitude_band | str | 'T' |
| sentinel:grid_square | str | 'GJ' |
| sentinel:sequence | str | '0' |
---
## USGS3DEP

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:epsg | int | 3857 |
| pc:type | str | 'lidar' |
| pc:points | int | 100000000 |
| pc:encoding | str | 'laszip' |
| legacy:span | int | 256 |
---
