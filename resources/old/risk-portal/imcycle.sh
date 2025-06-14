#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
echo "imcycle start"
pip3 install rtree
# sudo bash everestupdate.sh
python3 fbpull.py
python3 update.py
bash ./push.sh
echo "imcycle done"
cd $currentDir
