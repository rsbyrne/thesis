#!/bin/bash
currentDir=$PWD
if [[ $* == *-u* ]]
then
   sudo rm -rf book/_build
   python3 publishing/biblio.py
fi
#jb build book/
jb build book/ --builder pdflatex
#bash push.sh
cd $currentDir
