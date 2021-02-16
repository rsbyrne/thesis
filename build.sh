#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
docker build -t rsbyrne/thesis:latest .
docker push rsbyrne/thesis:latest
cd $currentDir
