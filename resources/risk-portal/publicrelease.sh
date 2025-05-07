#!/bin/bash

currentDir=$PWD
SCRIPT=`realpath $0`
DIRNAME="$(dirname "$SCRIPT")"
PUBLICREPO=$DIRNAME/../mobility-aus
cd $DIRNAME/products

echo "releasing public access data"

rm -f $PUBLICREPO/products/*
xargs -a ../publicrelease.txt cp -t $PUBLICREPO/products/
$PUBLICREPO/cycle.sh

echo "public access data released"

cd $currentDir
