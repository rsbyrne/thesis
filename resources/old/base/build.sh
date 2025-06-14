#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
docker build -t rsbyrne/base:latest .
docker push rsbyrne/base:latest
cd $currentDir
