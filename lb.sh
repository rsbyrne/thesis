#!/bin/bash
# exit when any command fails
set -e
currentDir=$PWD
cd "$(dirname "$0")"
MOUNTTO='/home/morpheus/workspace'
MOUNTFROM=$currentDir
FORCED=0
BUILD=0
SCRIPT="./init.sh"
while getopts m:c:p:s:fb flag
do
    case "${flag}" in
        m) MOUNTFROM=${OPTARG};;
        c) CAPTURES+=${OPTARG};;
        p) PYTHONADD+=${OPTARG};;
        s) SCRIPT=${OPTARG};;
        f) FORCED=1;;
        b) BUILD=1;;
    esac
done
if [[ $BUILD -eq 1 ]]
then
    ./build.sh
fi
mkdir -p $MOUNTFROM
OUTPUTFILE=$MOUNTFROM/vm.id
if [[ -f $OUTPUTFILE ]]
then
    DOCKERID=$(<$OUTPUTFILE)
    if docker inspect $DOCKERID > /dev/null
    then
        if [[ $FORCED -eq 1 ]]
        then
            docker rm -f $DOCKERID
        else
            echo "Looks like there is a VM is already running here"
            echo "(or a VM failed to exit properly):"
            echo "aborting startup."
            exit 1
        fi
    fi
fi
#chmod o+rw $MOUNTFROM
chown 15215 $MOUNTFROM
chgrp 17932 $MOUNTFROM
for CAPTURED in "${CAPTURES[@]}"; do
    CAPTURED=$MOUNTFROM/$CAPTURED
    chown -R 15215 $CAPTURED
    chgrp -R 17932 $CAPTURED
done
IMAGE='rsbyrne/everest:latest'
SOCK='/var/run/docker.sock'
> $OUTPUTFILE
docker run \
  -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK \
  --shm-size 2g -p 8888:8888 \
  --interactive --tty --detach \
  $IMAGE \
  $SCRIPT &> $OUTPUTFILE
cd $currentDir
