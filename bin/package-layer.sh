#!/bin/bash

# Directory used for deployment
export DEPLOY_DIR=layer

mkdir $DEPLOY_DIR

PYPATH=/var/lang/lib/python3.6/site-packages


echo Creating deployment package for cognition-datasources

# Moving python libraries
mkdir $DEPLOY_DIR/python
EXCLUDE="shapely* stac_validator* s3transfer* boto3* botocore* pip* docutils* *.pyc setuptools* wheel* coverage* testfixtures* mock* *.egg-info *.dist-info __pycache__ easy_install.py"

EXCLUDES=()
for E in ${EXCLUDE}
do
    EXCLUDES+=("--exclude ${E} ")
done

rsync -ax $PYPATH/ $DEPLOY_DIR/python/ ${EXCLUDES[@]}

cd $DEPLOY_DIR
zip -ruq ../lambda-layer.zip ./