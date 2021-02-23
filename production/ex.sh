#!/bin/bash

MOUNTTO='/home/jovyan/workspace'
IMAGE='rsbyrne/planetengine:latest'
docker run -u 0 -v $PWD:$MOUNTTO -d $IMAGE $*