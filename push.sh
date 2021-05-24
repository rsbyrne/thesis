#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
bash configure_ssh.sh
eval "$(ssh-agent)"
ssh-add ~/.ssh/*.pem
git add .
git commit -m "Quick push"
git push
ghp-import -n -p -f book/_build/html
cd $currentDir