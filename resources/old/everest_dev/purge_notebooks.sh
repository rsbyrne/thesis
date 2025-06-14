#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
python3 -m nbconvert --clear-output **/*.ipynb
cd $currentDir
