#!/bin/bash

MOUNTTO='/home/jovyan/workspace'
IMAGE='rsbyrne/planetengine:thesis'
docker run -d --detach-keys "ctrl-a,a" -u 0 -v $PWD:$MOUNTTO -p 7777:7777 $IMAGE $MOUNTTO/run_nb.sh
