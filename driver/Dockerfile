FROM geospatialjeff/cognition-datasources:latest

COPY requirements*.txt ./

# Paths to things
ENV \
    PROD_LIBS=/build/prod \
    PYTHONPATH=$PYTHONPATH:/$PROD_LIBS/lib/python3.6/site-packages:/home/cognition-datasources/spatial-db/lambda_db \
    LAMBDA_DB_PATH=/home/cognition-datasources/spatial-db/lambda_db/database.fs

# Install requirements into seperate folders
RUN \
    mkdir $PROD_LIBS; \
    pip install -r requirements-dev.txt; \
    pip install -r requirements.txt --install-option="--prefix=$PROD_LIBS" --ignore-installed;

COPY bin/* /usr/local/bin/

# Giving exec permissions to script
RUN \
    chmod +x /usr/local/bin/driver-package.sh

WORKDIR /home/cognition-datasources