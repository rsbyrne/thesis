#!/bin/bash

MOUNTTO='/home/jovyan/workspace'
IMAGE='rsbyrne/planetengine:latest'
docker run -u 0 --detach-keys "ctrl-a,a" -v $PWD:$MOUNTTO -it $IMAGE bash
