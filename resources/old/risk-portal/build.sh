#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
#sh push.sh
docker build -t rsbyrne/risk-portal:latest .
docker push rsbyrne/risk-portal:latest
cd $currentDir
