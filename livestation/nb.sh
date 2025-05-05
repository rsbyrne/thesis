#!/bin/bash

MOUNTTO='/home/jovyan/workspace'
IMAGE='rsbyrne/planetengine:thesis'
docker run -u 0 -v $PWD:$MOUNTTO -p 7777:7777 $IMAGE \
  jupyter notebook --no-browser --allow-root --port=7777 --ip='0.0.0.0'
