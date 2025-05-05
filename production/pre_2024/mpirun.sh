#!/bin/bash

INTERPRETER=python3
DATE=$(date +%s)
oldIFS="$IFS"
IFS="-"
OUTFILE="$*""."$DATE".out"
ERRORFILE="$*""."$DATE".error"
IFS=$oldIFS
mpirun -np $2 $INTERPRETER $1 ${@: 3} 1> $OUTFILE 2> $ERRORFILE &
