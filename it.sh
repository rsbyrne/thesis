#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/thesis'
SOCK='/var/run/docker.sock'
docker run -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK -it --shm-size 2g $IMAGE bash
cd $currentDir
