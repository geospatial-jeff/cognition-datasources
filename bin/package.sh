#!/bin/bash

# Directory used for deployment
export DEPLOY_DIR=lambda

PYPATH=/var/lang/lib/python3.6/site-packages


echo Creating deployment package for cognition-datasources

# Moving libs
mkdir -p $DEPLOY_DIR/lib
cp -P /usr/lib64/libspatialindex* $DEPLOY_DIR/lib
strip $DEPLOY_DIR/lib/* || true

# Moving python libraries
mkdir $DEPLOY_DIR/python
EXCLUDE="boto3* botocore* pip* docutils* *.pyc setuptools* wheel* coverage* testfixtures* mock* *.egg-info *.dist-info __pycache__ easy_install.py"

EXCLUDES=()
for E in ${EXCLUDE}
do
    EXCLUDES+=("--exclude ${E} ")
done

rsync -ax $PYPATH/ $DEPLOY_DIR/python/ ${EXCLUDES[@]}


cd $DEPLOY_DIR
zip -ruq ../lambda-deploy.zip ./