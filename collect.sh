#!/bin/bash
echo "Collecting..."
currentDir=$PWD
cd "$(dirname "$0")"/dropbox
eval "$(ssh-agent)"
ssh-add ~/.ssh/*.pem
scp -i ~/.ssh/general.pem -r ubuntu@172.26.134.68:~/volume/dropbox/* .
scp -i ~/.ssh/general.pem -r ubuntu@172.26.131.135:~/volume/thesis/dropbox/* .
cd $currentDir
echo "All collected."