FROM geospatialjeff/cognition-datasources:latest

COPY requirements*.txt ./

# Paths to things
ENV \
    PROD_LIBS=/build/prod \
    DEV_LIBS=/build/dev

# Add libraries to python path
ENV \
    PYTHONPATH=$PYTHONPATH:/$PROD_LIBS/lib/python3.6/site-packages:/$DEV_LIBS/lib/python3.6/site-packages

# Install requirements into seperate folders
RUN \
    mkdir prod; \
    mkdir dev; \
    pip install -r requirements.txt --install-option="--prefix=$PROD_LIBS" --ignore-installed; \
    pip install -r requirements-dev.txt --install-option="--prefix=$DEV_LIBS" --ignore-installed

COPY bin/* /usr/local/bin/