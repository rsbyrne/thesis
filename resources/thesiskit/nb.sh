#!/bin/bash

MOUNTTO='/home/jovyan/workspace'
IMAGE='rsbyrne/planetengine:thesis'
docker run -u 0 -v $PWD:$MOUNTTO -p 8889:8889 $IMAGE \
  jupyter notebook --no-browser --allow-root --port=8889 --ip='0.0.0.0'
