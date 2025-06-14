#!/bin/bash
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/base'
docker run -v $MOUNTFROM:$MOUNTTO -it $IMAGE bash
