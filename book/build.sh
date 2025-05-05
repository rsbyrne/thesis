#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
myst build --pdf
cd $currentDir
