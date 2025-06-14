#!/bin/bash
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/base'
docker run -u 0 -v $MOUNTFROM:$MOUNTTO -it $IMAGE bash
