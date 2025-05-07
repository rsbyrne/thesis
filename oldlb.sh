#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/thesis'
SOCK='/var/run/docker.sock'
SHMSIZE='64m'
docker run -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK --shm-size $SHMSIZE -p 8888:8888 $IMAGE \
  jupyter lab --no-browser --allow-root --port=8888 --ip='0.0.0.0'
cd $currentDir
