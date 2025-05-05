#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"/main
myst build --pdf
cd $currentDir
