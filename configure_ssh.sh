#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
sudo rm -r ~/.ssh/*
mkdir ~/.ssh/
cp -f *.pem ~/.ssh/
sudo chmod 700 ~/.ssh/
sudo chmod 600 ~/.ssh/*
eval "$(ssh-agent)"
ssh-add ~/.ssh/*.pem
cd $currentDir
