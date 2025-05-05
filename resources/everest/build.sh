#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
docker build -t rsbyrne/everest:latest .
docker push rsbyrne/everest:latest
cd $currentDir
