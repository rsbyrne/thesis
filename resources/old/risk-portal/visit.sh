#!/bin/bash

filedir="$(dirname "$0")"

cd filedir
bash configure_ssh.sh
ssh -o IPQoS=throughput -i ~/.ssh/general.pem ubuntu@45.113.232.139
