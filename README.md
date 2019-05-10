## About

This library defines a pluggable, STAC-compliant, service for searching geospatial assets, primarily remotely sensed imagery, and serves two primary purposes:

#### 1. Define a pluggable driver interface (similar to GraphQL resolvers) for wrapping the STAC spec around legacy datasources.
#### 2. Provide a framework for loading / executing drivers both locally and in the cloud.

Each driver translates the STAC-compliant request into a format compatible with the underlying API while translating the API response to a valid STAC Item.  Drivers are packaged and deployed to AWS Lambda and a single API Gateway endpoint is created which allows searching the loaded datasources.  The goal is to create an extensible service which allows users to integrate their datasets with the STAC ecosystem without having to change how their data is stored and queried.

![title](docs/images/api-diagram.png)

## Installation
```
git clone https://github.com/geospatial-jeff/cognition-datasources
cd cognition-datasources
python setup.py install
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

## Testing
Each driver must pass a [standard set of test cases](./datasources/tests.py) and uses CircleCI to ensure only working drivers are loaded into the library.  View the status of each driver [here](./docs/datasource-status.md).

## Contributing
Check out the [contributing docs](./docs/contributing.md) for step-by-step guide for building your own driver.
