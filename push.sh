#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
# bash configure_ssh.sh
eval "$(ssh-agent)"
ssh-add ~/.ssh/*.pem
# python3 -m nbconvert --clear-output working/*.ipynb dev/*.ipynb scratch/*.ipynb analysis/*.ipynb
git config --global user.email "rohan.byrne@gmail.com"
git config --global user.name "rsbyrne"
git add .
git commit -m "Quick push"
git push
#ghp-import -n -p -f book/_build/html
cd $currentDir
