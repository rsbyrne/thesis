#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
# mkdir ~/.ssh/
sudo rm -r ~/.ssh/*
cp -f *.pem ~/.ssh/
sudo chmod 700 ~/.ssh/
sudo chmod 600 ~/.ssh/*.pem
eval "$(ssh-agent)"
ssh-add ~/.ssh/*.pem
git config --global url.ssh://git@github.com/.insteadOf https://github.com/
cd $currentDir
