#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
mkdir ~/.ssh/
sudo rm -r ~/.ssh/*
cp -f *.pem ~/.ssh/
sudo chmod 700 ~/.ssh/
sudo chmod 600 ~/.ssh/*
# eval "$(ssh-agent)"
# ssh-add ~/.ssh/*.pem
cd $currentDir
