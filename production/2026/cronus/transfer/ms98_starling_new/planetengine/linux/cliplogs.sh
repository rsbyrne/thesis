#!/bin/bash
umask 0000
FILE=${1}
LINES=${2:-100}
echo "$(tail -$LINES $FILE)" > $FILE
