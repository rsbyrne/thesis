#!/bin/bash
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/scibase'
SOCK='/var/run/docker.sock'
docker run -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK --shm-size 2g -p 8888:8888 $IMAGE \
  jupyter lab --no-browser --allow-root --port=8888 --ip='0.0.0.0'
