# cognition-datasources

[![CircleCI](https://circleci.com/gh/geospatial-jeff/cognition-datasources/tree/master.svg?style=svg)](https://circleci.com/gh/geospatial-jeff/cognition-datasources/tree/master)

## About
This library defines a STAC-compliant standardized interface for searching geospatial assets, primarily remotely sensed imagery.  The [Spatio-Temporal-Asset-Catalog (STAC)](https://github.com/radiantearth/stac-spec) specification provides common metadata and API schemas to search and access geospatial data.  The standardized interface used by the library is based on the STAC spec and allows searching across three dimensions:

- **Spatial:** Find all assets which intersect a bounding box.
- **Temporal:** Find all assets acquired within a temporal window.
- **Properties:** Find all assets with certain  metadata.

Not all commonly used datasources are currently STAC-compliant.  In such cases, the library maintains a standardized search interface by wrapping the API with a STAC-compatible API which parses the initial search parameters into a format compatible with the underlying API.  A request to the API is sent and the response is parsed into a STAC Item and returned to the user.  The table below of supported datasources states which are STAC-compliant.

![title](docs/images/api-diagram.png)

#### Datasource Drivers
The interface defined by the library is extended by datasource drivers which are defined in external github repositories and loaded into the library through a command line interface.  Similar to how drivers control hardware, the logic implemented in the datasource driver influences how cognition-datasources accesses the underlying datasource.  Each driver is expected to follow a specific pattern and pass a standard set of test cases (enforced with CircleCI).  Check out the [contribution guidelines](/docs/contributing.md) for a guide on how to develop your own datasource driver!


## Setup
```
# Install library
pip install git+https://github.com/geospatial-jeff/cognition-datasources

# Load datasources
cognition-datasources load -d Landsat8 -d Sentinel2
```

## Usage

#### Python
```python
from datasources import Manifest

# Create manifest
manifest = Manifest()

# Search arguments
spatial = {"type": "Polygon", "coordinates": [[...]]}
temporal = ("2018-10-30", "2018-12-31")
properties = {'eo:cloud_cover': {'lt': 10}}

# Create searches for Landsat8 and Sentinel2
manifest['Landsat8'].search(spatial, temporal=temporal, properties=properties)
manifest['Sentinel2'].search(spatial, temporal=temporal, properties=properties)

# Execute searches
response = manifest.execute()
```

#### CLI
```
cognition-datasources search xmin ymin xmax ymax --start-date "2018-10-30" --end-date "2018-12-31" -d Landsat8 -d Sentinel2 --output response.json
```

## Testing
Each driver must pass a [standard set of test cases](datasources/tests.py) and uses CircleCI to ensure only working drivers are loaded into the library.

## Documentation
Read the [quickstart](./docs/quickstart.ipynb) and [documentation](./docs).

## Supported Datasource Drivers
| Name | Source | STAC-Compliant | Notes |
|----------------|--------------------------------------------------------------------------|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [DGOpenData](https://github.com/geospatial-jeff/cognition-datasources-dgopendata) | [Digital Globe Open Data Program](https://www.digitalglobe.com/ecosystem/open-data) | False | Builds index with a [web scraper](https://github.com/geospatial-jeff/dg-open-data-scraper). |
| [ElevationTiles](https://github.com/geospatial-jeff/cognition-datasources-elevationtiles) | [AWS Earth: Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) | False | Sends header requests to AWS S3 Bucket. |
| [CBERS](https://github.com/geospatial-jeff/cognition-datasources-cbers) | [AWS Earth: CBERS](https://registry.opendata.aws/cbers/) | False | Sends requests to AWS S3 Bucket (**RequesterPays**) with help of [aws-sat-api](https://github.com/RemotePixel/aws-sat-api-py). |
| [Landsat8](https://github.com/geospatial-jeff/cognition-datasources-landsat8) | [AWS Earth: Landsat8](https://registry.opendata.aws/landsat-8/) | True | Sends requests to [sat-api]( https://github.com/sat-utils/sat-api). |
| [NAIP](https://github.com/geospatial-jeff/cognition-datasources-naip) | [AWS Earth: NAIP](https://registry.opendata.aws/naip/) | False | Sends requests to AWS S3 Bucket (**RequesterPays**). |
| [Sentinel1](https://github.com/geospatial-jeff/cognition-datasources-sentinel1) | [Copernicus Open Access Hub](https://scihub.copernicus.eu/) | False | Sends requests to [CopernicusAPIHub](https://scihub.copernicus.eu/twiki/do/view/SciHubWebPortal/APIHubDescription) with help of [sentinelsat](https://github.com/sentinelsat/sentinelsat). |
| [Sentinel2](https://github.com/geospatial-jeff/cognition-datasources-sentinel2) | [AWS Earth: Sentinel2](https://registry.opendata.aws/sentinel-2/) | True | Sends requests to [sat-api](https://github.com/sat-utils/sat-api). |
| [SRTM](https://github.com/geospatial-jeff/cognition-datasources-srtm) | [AWS: Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) | False | Does not send any requests. |
| [USGS 3DEP](https://github.com/geospatial-jeff/cognition-datasources-usgs3dep) | [AWS: USGS 3DEP](https://registry.opendata.aws/usgs-lidar/) | False | Sends request to AWS S3 Bucket. |
| [Microsoft Building Footprints](https://github.com/geospatial-jeff/cognition-datasources-mbf) | [Microsoft](https://github.com/Microsoft/USBuildingFootprints) / [ESRI](https://www.arcgis.com/home/item.html?id=f40326b0dea54330ae39584012807126) | False | Sends requests to ESRI Feature Layer |