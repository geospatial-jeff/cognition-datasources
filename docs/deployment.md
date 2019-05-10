# Deployment
The purpose of this page is to explain how to deploy your own instance of cognition-datasources.  The library may be deployed to either the cloud (via [Serverless Framework](https://serverless.com/)) or locally.  The cloud deployment packages each driver as an AWS Lambda function while the local deployment installs drivers to your local installation of cognition-datasources.  For more information see [How It Works](./contributing.md#how-it-works)

Drivers which also package spatial coverages are currently not compatible with local installations.

## Cloud Deployment (AWS Lambda + API Gateway)
**(1). Clone the library and install the CLI.**

```
git clone https://github.com/geospatial-jeff/cognition-datasources my-cd-deployment
cd my-cd-deployment
python setup.py install
```

**(2). Load datasources into your deployment.**

```
cognition-datasources -d Landsat8 -d Sentinel2
```

This command will populate `serverless.yml` and `handler.py` with all of the necessary configuration and code to create the service.  Each driver is packaged as its own lambda function.

**(3). Build docker container**

```
docker build . -t cognition-datasources:latest
```

**(4). Package service**

```
docker run --rm -v $PWD:/home/cognition-datasources -it cognition-datasources:latest package-service.sh
```

**(5). Edit the configuration variables in `serverless.yml`**

**(6). Deploy the service to AWS via Serverless Framework**

```
sls deploy -v
```

The deployment generates an AWS API Gateway endpoint which supports STAC-compliant searches of the loaded datasources through the `/stac/search` endpoint (POST).


## Local Deployment
**(1). Clone the library and install the CLI.**

```
git clone https://github.com/geospatial-jeff/cognition-datasources my-cd-deployment
cd my-cd-deployment
python setup.py install
```

**(2). Load datasources into your deployment while enabling the `local` flag.**

```
cognition-datasources -d Landsat8 -d Sentinel2 --local
```

While the local flag is enabled, the driver and its dependencies will be installed locally.  The driver is stored in the `./datasources/sources/` folder while all dependencies are installed to the default location of the current environment.
