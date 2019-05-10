### Create base lambda layer
1. Create deployment zipfile.
```
docker build . -t cognition-datasources:latest
docker run --rm -v $PWD:/home/cognition-datasources -it cognition-datasources:latest package.sh
```

2. Push as lambda layer.
```
aws lambda publish-layer-version \
    --layer-name cognition-datasources \
    --description "Base layer for cognition-datasources" \
    --zip-file fileb://lambda-deploy.zip
```

3. Make layer public.
```
aws lambda add-layer-version-permission --layer-name cognition-datasources \
    --statement-id public --version-number 1 --principal '*' \
    --action lambda:GetLayerVersion
```