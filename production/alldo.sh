#!/bin/bash

DIR="$(dirname "$0")"

DESTS=(\
  "pluto1" \
  "charon1" \
  "charon2" \
  "charon3" \
  "charon4" \
  "charon5" \
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
  echo $DEST
  bash $DIR/goto.sh $DEST "$*"
done