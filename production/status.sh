#!/bin/bash

s_flag='false'
while getopts 's' flag; do
  case "${flag}" in
    s) s_flag='true' ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

if [ s_flag = 'true']; then
  COMMAND="top -n 1 -b | head -n 32 && ls -lht *working/*.out | wc -l && ls -lht *working/*.out && df -h"
else
  COMMAND="ls && ls -lht *working/*.out | wc -l"
fi

ADDRESSES=(\
  45.113.235.136 \
  45.113.233.242 \
  45.113.233.237 \
  45.113.233.238 \
  45.113.235.186 \
  45.113.233.246 \
  45.113.235.111 \
  45.113.235.59 \
  45.113.232.139 \
  115.146.93.171 \
  115.146.95.143 \
  115.146.93.145 \
  45.113.235.87 \
  115.146.95.188\
  )

for ADDRESS in ${ADDRESSES[@]}; do
  echo " "
  echo "-------------------------------"
  echo $ADDRESS
  ssh -o IPQoS="throughput" -i "~/.ssh/general.pem" "ubuntu@"$ADDRESS $COMMAND
done
