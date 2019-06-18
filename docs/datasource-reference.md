[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-cbers.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-cbers)

## CBERS

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [limit, subdatasets] |

* The `subdatasets` kwarg allows querying by sensor (mux, awfi, pan5m, and pan10m).

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 20.0 |
| eo:epsg | int | 32614 |
| eo:platform | str | 'CBERS' |
| eo:sun_azimuth | float | 154.88 |
| eo:sun_elevation | float | 28.26 |
| eo:off_nadir | float | 0.004 |
| cbers:data_type | str | 'L2' |
| cbers:path | int | 229 |
| cbers:row | int | '48 |
---
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-dgopendata.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-dgopendata)

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
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-elevationtiles.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-elevationtiles)
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
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-landsat8.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-landsat8)

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
| landsat:product_id | str | 'LC08_L1TP_032028_20190616_20190617_01_RT' |
| landsat:scene_id | str | 'LC80320282019167LGN00' |
| landsat:tier | str | 'RT' |
| landsat:revision | str | '00' |
---
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-mbf.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-mbf)

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
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-naip.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-naip)

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
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-planet.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-planet)

## PlanetData

| Parameter | Status |
| ----------| ------ |
| Spatial | :heavy_check_mark: |
| Temporal | :heavy_check_mark: |
| Properties | :heavy_check_mark: |
| **kwargs | [subdatasets] |

##### Properties
| Property | Type | Example |
|--------------------------|-------|-------------|
| eo:gsd | float | 0.9 |
| eo:instrument | str | 'SSC1' |
| eo:off_nadir | float | 26.3 |
| eo:instrument | str | 'SSC1' |
| eo:azimuth | float | 163.4 |
| eo:sun_azimuth | int | 139 |
| eo:sun_elevation | float | 70.1 |
| eo:cloud_cover | float | 0.06 |
| legacy:camera_id | str | 'd2' |
| legacy:ground_conrol | bool | true |
| legacy:item_type | str | 'SkySatScene' |
| legacy:provider | str | 'skysat' |
| legacy:published | str | "2019-05-13T04:50:40.092Z" |
| legacy:quality_category | str | "standard" |
| legacy:strip_id | str | 's3_20190512T185450Z' |
| legacy:updated | str | '2019-06-01T19:14:40.178Z' |




---
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-sentinel1.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-sentinel1)

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
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-sentinel2.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-sentinel2)

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
| eo:gsd | int | 10 |
| eo:epsg | int | 32614 |
| eo:instrument | str | 'MSI' |
| eo:platform | str | 'sentinel-2b' |
| eo:off_nadir | int | 0 |
| eo:cloud_cover | int | 100 |
| sentinel:utm_zone | int | 13 |
| sentinel:latitude_band | str | 'T' |
| sentinel:grid_square | str | 'GJ' |
| sentinel:sequence | str | '0' |
---
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-srtm.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-srtm)

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
[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources-usgs3dep.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources-usgs3dep)

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
