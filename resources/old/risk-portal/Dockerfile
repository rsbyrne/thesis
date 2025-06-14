FROM rsbyrne/everest
MAINTAINER https://github.com/rsbyrne/

USER root

# Visualisation
RUN pip3 install --no-cache-dir bokeh

# Geographic
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  libspatialindex-dev \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U --no-cache-dir \
  shapely \
  fiona \
  descartes \
  geopandas \
  mercantile \
  rasterio \
  rtree

# Web
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  unzip \
  firefox \
  firefox-geckodriver \
  && rm -rf /var/lib/apt/lists/*

# WORKDIR /usr/bin
# RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz && tar -xvzf geckodriver* && rm geckodriver*.tar.gz && chmod +x geckodriver

RUN pip3 install -U --no-cache-dir \
#   Flask \
  selenium

# RUN pip3 install -U --no-cache-dir \
#   tables \
#   pyarrow

# Finish
RUN apt update -y && apt upgrade -y

WORKDIR $MOUNTDIR
USER $MASTERUSER
