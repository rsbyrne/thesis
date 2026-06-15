#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <command> <number_of_times>"
    exit 1
fi

COMMAND=$1
TIMES=$2

for (( i=1; i<=$TIMES; i++ ))
do
    echo "Running command $i of $TIMES"
    eval $COMMAND
done

echo "Command executed $TIMES times."