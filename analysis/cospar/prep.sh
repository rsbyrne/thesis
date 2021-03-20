#!/bin/bash
DIR="$(dirname "$0")"
python3 $DIR"/merge.py"
python3 $DIR"/obsvisc.py"
