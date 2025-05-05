#!/bin/bash

DIR="$(dirname "$0")"
ADDRESS=$(bash $DIR/address.sh $1)

ssh -o IPQoS="throughput" -i "~/.ssh/general.pem" "ubuntu@"$ADDRESS $2
