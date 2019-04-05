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

# Installing libspatialindex
RUN \
    mkdir rtree-config; \
    cd rtree-config; \
    wget http://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/s/spatialindex-1.8.5-1.el7.x86_64.rpm; \
    yum install -y spatialindex-1.8.5-1.el7.x86_64.rpm; \
    cd ..; rm -rf rtree-config;

# Installing geos
RUN \
    yum install -y geos-devel;


# Installing cognition-datasources + requirements
COPY requirements.txt ./

RUN \
    pip install -r requirements.txt; \
    pip install git+https://github.com/geospatial-jeff/cognition-datasources.git


# Copy shell scripts
COPY bin/* /usr/local/bin/

WORKDIR /home/cognition-datasources