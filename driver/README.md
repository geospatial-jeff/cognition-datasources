# External Drivers

1. Add driver requirements to `requirements.txt` and `requirements-dev.txt`
2. Build docker image

```
docker build . -t <driver-name>:latest
```

3. Run test cases inside docker container

```
docker run --rm -v $PWD:/home/cognition-datasources -it <driver-name>:latest python -m unittest tests.py
```

4. Build lambda layer

```
docker run --rm -v $PWD:/home/cognition-datasources -it <driver-name<:latest driver-package.sh <driver-name>
```

5. Deploy layer to lambda
```
aws lambda publish-layer-version \
    --layer-name <driver-name> \
    --zip-file fileb://lambda-deploy.zip
```

6. Make layer public (do this after deploying a new version)
```
aws lambda add-layer-version-permission --layer-name <driver-name> \
    --statement-id public --version-number 1 --principal '*' \
    --action lambda:GetLayerVersion
```

