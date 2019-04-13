#!/bin/bash

# Directory used for deployment
export DEPLOY_DIR=service

mkdir $DEPLOY_DIR

# Moving handler
cp handler.py $DEPLOY_DIR

cd $DEPLOY_DIR
zip -ruq ../lambda-service-package.zip ./