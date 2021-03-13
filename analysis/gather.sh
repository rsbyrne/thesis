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
  ADDRESS=""
  case "$DEST" in
    pluto1) ADDRESS="45.113.235.136" ;;
    pluto2) ADDRESS="45.113.233.242" ;;
    pluto3) ADDRESS="45.113.233.237" ;;
    pluto4) ADDRESS="45.113.233.238" ;;
    pluto5) ADDRESS="45.113.235.186" ;;
    pluto6) ADDRESS="45.113.233.246" ;;
    miranda1) ADDRESS="45.113.235.111" ;;
    miranda2) ADDRESS="45.113.235.59" ;;
    umbriel1) ADDRESS="45.113.232.139" ;;
    umbriel2) ADDRESS="115.146.93.171" ;;
    umbriel3) ADDRESS="115.146.95.143" ;;
    umbriel4) ADDRESS="115.146.93.145" ;;
    umbriel5) ADDRESS="45.113.235.87" ;;
    umbriel6) ADDRESS="115.146.95.188" ;;
  esac
  mkdir $DIR/$DEST/
  scp -v -o IPQoS="throughput" -i ~/.ssh/general.pem ubuntu@$ADDRESS:~/*working/*.frm $DIR/$DEST/
done