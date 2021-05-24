#!/bin/bash
eval "$(ssh-agent)"
ssh-add ~/.ssh/*.pem
currentDir=$PWD
if [[ $* == *-u* ]]
then
   sudo rm -rf book/_build
   python3 publishing/biblio.py
fi
jb build -W -n --keep-going book/
# jb build book/ --builder pdflatex
ghp-import -n -p -f book/_build/html
cd $currentDir