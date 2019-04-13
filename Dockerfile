FROM lambci/lambda:build-python3.6


# Installing system libraries
RUN \
    yum install -y wget; \
    yum clean all; \
    yum autoremove;


# Paths
ENV \
    PREFIX=/usr/local \
    LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64

# Switch to build directory
WORKDIR /build

# Installing geos
RUN \
    yum install -y geos-devel;


# Installing cognition-datasources + requirements
COPY requirements.txt ./

RUN \
    pip install -r requirements.txt; \
    pip install git+https://github.com/geospatial-jeff/cognition-datasources.git@lambda_layers


# Copy shell scripts
COPY bin/* /usr/local/bin/

WORKDIR /home/cognition-datasources