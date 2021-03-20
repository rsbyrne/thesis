#!/bin/bash

DIR="$(dirname "$0")"

bash $DIR/alldo.sh "for F in \$(ls *working/*.out); do sudo truncate -s 0 \$F; done"
