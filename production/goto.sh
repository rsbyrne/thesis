#!/bin/bash

ADDRESS=""
case "$1" in
  pluto1) ADDRESS="45.113.232.99" ;;
  pluto2) ADDRESS="45.113.233.242" ;;
  pluto3) ADDRESS="45.113.233.237" ;;
  pluto4) ADDRESS="45.113.233.238" ;;
  pluto5) ADDRESS="45.113.235.186" ;;
  pluto6) ADDRESS="45.113.233.246" ;;
  miranda1) ADDRESS="45.113.235.100" ;;
  miranda2) ADDRESS="45.113.233.217" ;;
  umbriel1) ADDRESS="45.113.232.139" ;;
  umbriel2) ADDRESS="115.146.93.171" ;;
  umbriel3) ADDRESS="115.146.95.143" ;;
  umbriel4) ADDRESS="115.146.93.145" ;;
  umbriel5) ADDRESS="45.113.235.87" ;;
  umbriel6) ADDRESS="115.146.95.188" ;;
esac

ssh -o IPQoS="throughput" -i "~/.ssh/general.pem" "ubuntu@"$ADDRESS $2