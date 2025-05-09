#!/bin/bash

DIR="$(dirname "$0")"

v_flag='false'
while getopts 'v' flag; do
  case "${flag}" in
    v) v_flag='true' ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

DESTS=(\
  "pluto1" \
  "pluto2" \
  "pluto3" \
  "pluto4" \
  "pluto5" \
  "pluto6" \
  "miranda1" \
  "miranda2" \
  "umbriel1" \
  "umbriel2" \
  "umbriel3" \
  "umbriel4" \
  "umbriel5" \
  "umbriel6"\
  )

for DEST in ${DESTS[@]}; do
  COMMAND="echo .out files: && ls -lht $DEST'_working'/plasticfull.py-17*.out | wc -l && echo .error files: && find $DEST'_working' -type f -name 'plasticfull.py-17*.error' -size +0 -ls | wc -l && echo processes: && ps -C python3 | wc -l"
  if [ $v_flag = 'true' ]; then
    COMMAND="top -n 1 -b | head -n 32 && $COMMAND && df -h"
  fi
  echo " "
  echo "-------------------------------"
  echo $DEST
  bash $DIR"/""goto.sh" $DEST "$COMMAND"
done
