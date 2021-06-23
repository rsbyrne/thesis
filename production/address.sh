#!/bin/bash

ADDRESS=""
case "$1" in
  pluto1) ADDRESS="45.113.232.99" ;;
  charon1) ADDRESS="45.113.235.31" ;;
  charon2) ADDRESS="45.113.235.38" ;;
  charon3) ADDRESS="45.113.235.141" ;;
  charon4) ADDRESS="45.113.235.23" ;;
  charon5) ADDRESS="45.113.233.148" ;;
  miranda1) ADDRESS="45.113.235.100" ;;
  miranda2) ADDRESS="45.113.233.217" ;;
  umbriel1) ADDRESS="45.113.232.139" ;;
  umbriel2) ADDRESS="115.146.93.171" ;;
  umbriel3) ADDRESS="115.146.95.143" ;;
  umbriel4) ADDRESS="115.146.93.145" ;;
  umbriel5) ADDRESS="45.113.235.87" ;;
  umbriel6) ADDRESS="115.146.95.188" ;;
esac

echo $ADDRESS
