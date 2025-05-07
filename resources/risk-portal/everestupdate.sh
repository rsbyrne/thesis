#!/bin/bash

currentDir=$PWD
cd "$(dirname "$0")"

bash configure_ssh.sh
eval "$(ssh-agent)" && ssh-add ~/.ssh/*.pem
cd ..
sudo rm -rf ./everest
cp -r mount/everest .
cd everest
git pull
bash push.sh
cd ..
sudo rm -rf mount/everest
cp -r everest/ mount/

cd $currentDir
