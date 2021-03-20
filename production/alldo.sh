#!/bin/bash

DIR="$(dirname "$0")"

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
  bash $DIR/goto.sh $DEST "$*"
done