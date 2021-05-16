#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
python3 search.py "$*"
cd $currentDir