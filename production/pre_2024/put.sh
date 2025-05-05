#!/bin/bash

DIR="$(dirname "$0")"
ADDRESS=$(bash $DIR/address.sh $1)

scp -v -o IPQoS="throughput" -i ~/.ssh/general.pem $2 ubuntu@$ADDRESS:$3
