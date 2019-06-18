## About

This library defines a pluggable, STAC-compliant, service for searching geospatial assets, primarily remotely sensed imagery, and serves two primary purposes:

1. Define a pluggable driver interface (similar to GraphQL resolvers) for wrapping the STAC spec around legacy datasources.
2. Provide a framework for loading / executing drivers both locally and in the cloud.

Each driver translates the STAC-compliant request into a format compatible with the underlying API while translating the API response to a valid STAC Item.  Drivers are packaged and deployed to AWS Lambda and a single API Gateway endpoint is created which allows searching the loaded datasources.  The goal is to create an extensible service which allows users to integrate their datasets with the STAC ecosystem without having to change how their data is stored and queried.

![title](docs/images/service-diagram.png?style=centerme)

## Installation
```
git clone https://github.com/geospatial-jeff/cognition-datasources
cd cognition-datasources
python setup.py develop
```

## Deployment
```
# Load datasources
cognition-datasources -d Landsat8 -d Sentinel2 -d SRTM -d NAIP

# Build docker container
docker build . -t cognition-datasources:latest

# Package service
docker run --rm -v $PWD:/home/cognition-datasources -it cognition-datasources:latest package-service.sh

# Deploy to AWS
sls deploy -v
```
Read the [deployment docs](./docs/deployment.md) for more information on deployment.

## Usage
The deployment generates an AWS API Gateway endpoint which supports STAC-compliant searches of the loaded datasources through the `/stac/search` endpoint (POST).  Read the [API docs](./docs/README.md) for usage details.

A live example lives [here](https://github.com/geospatial-jeff/cognition-datasources-api).

## Testing
Each driver must pass a [standard set of test cases](./datasources/tests.py) and uses CircleCI to ensure only working drivers are loaded into the library.  View the status of each driver [here](./docs/datasource-status.md).

## Contributing
Check out the [contributing docs](./docs/contributing.md) for step-by-step guide for building your own driver.

## Supported Datasource Drivers
| Name | Source | STAC-Compliant | Notes |
|----------------|--------------------------------------------------------------------------|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [DGOpenData](https://github.com/geospatial-jeff/cognition-datasources-dgopendata) | [Digital Globe Open Data Program](https://www.digitalglobe.com/ecosystem/open-data) | False | Builds index with a [web scraper](https://github.com/geospatial-jeff/dg-open-data-scraper). |
| [ElevationTiles](https://github.com/geospatial-jeff/cognition-datasources-elevationtiles) | [AWS Earth: Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) | False | Sends header requests to AWS S3 Bucket. |
| [CBERS](https://github.com/geospatial-jeff/cognition-datasources-cbers) | [AWS Earth: CBERS](https://registry.opendata.aws/cbers/) | False | Sends requests to [earth-search](https://www.element84.com/earth-search/) |
| [Landsat8](https://github.com/geospatial-jeff/cognition-datasources-landsat8) | [AWS Earth: Landsat8](https://registry.opendata.aws/landsat-8/) | True | Sends requests to [earth-search](https://www.element84.com/earth-search/). |
| [NAIP](https://github.com/geospatial-jeff/cognition-datasources-naip) | [AWS Earth: NAIP](https://registry.opendata.aws/naip/) | False | Sends requests to AWS S3 Bucket (**RequesterPays**). |
| [PlanetData](https://github.com/geospatial-jeff/cognition-datasources-planet) | [Planet Data API](https://developers.planet.com/docs/api/) | False | Sends request to the [Planet Python Client](https://github.com/planetlabs/planet-client-python) |
| [Sentinel1](https://github.com/geospatial-jeff/cognition-datasources-sentinel1) | [Copernicus Open Access Hub](https://scihub.copernicus.eu/) | False | Sends requests to [CopernicusAPIHub](https://scihub.copernicus.eu/twiki/do/view/SciHubWebPortal/APIHubDescription) with help of [sentinelsat](https://github.com/sentinelsat/sentinelsat). |
| [Sentinel2](https://github.com/geospatial-jeff/cognition-datasources-sentinel2) | [AWS Earth: Sentinel2](https://registry.opendata.aws/sentinel-2/) | True | Sends requests to [earth-search](https://www.element84.com/earth-search/). |
| [SRTM](https://github.com/geospatial-jeff/cognition-datasources-srtm) | [AWS: Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) | False | Does not send any requests. |
| [USGS 3DEP](https://github.com/geospatial-jeff/cognition-datasources-usgs3dep) | [AWS: USGS 3DEP](https://registry.opendata.aws/usgs-lidar/) | False | Sends request to AWS S3 Bucket. |
| [Microsoft Building Footprints](https://github.com/geospatial-jeff/cognition-datasources-mbf) | [Microsoft](https://github.com/Microsoft/USBuildingFootprints) / [ESRI](https://www.arcgis.com/home/item.html?id=f40326b0dea54330ae39584012807126) | False | Sends requests to ESRI Feature Layer |

