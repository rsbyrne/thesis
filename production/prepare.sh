#!/bin/bash

DIR="$(dirname "$0")"

bash $DIR/do.sh $1 "sudo rm -rf $1_working/ && git clone https://github.com/rsbyrne/thesiskit && mv thesiskit $1_working && sudo docker system prune -af && sudo docker pull rsbyrne/planetengine:thesis"

bash $DIR/put.sh $1 "linear3_ins.py" $1_working/