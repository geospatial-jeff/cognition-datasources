#!/bin/bash

# directory used for deployment
export DEPLOY_DIR=lambda

DRIVERNAME=__TEMPLATENAME__
PYPATH=$PROD_LIBS/lib/python3.6/site-packages

echo "Creating lambda layer"

# Moving python libraries
mkdir -p $DEPLOY_DIR/python
EXCLUDE="click* urllib3* s3transfer* boto3* botocore* pip* docutils* *.pyc setuptools* wheel* coverage* testfixtures* mock* *.egg-info *.dist-info __pycache__ easy_install.py"


EXCLUDES=()
for E in ${EXCLUDE}
do
    EXCLUDES+=("--exclude ${E} ")
done

rsync -ax $PYPATH/ $DEPLOY_DIR/python/ ${EXCLUDES[@]}

# Copying driver to cognition-datasources folder
mkdir -p $DEPLOY_DIR/python/datasources/sources/
cp $DRIVERNAME.py $DEPLOY_DIR/python/datasources/sources/


# Make lambda layer
cd $DEPLOY_DIR
zip -ruq ../lambda-layer.zip ./
