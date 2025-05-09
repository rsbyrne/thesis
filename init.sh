#!/bin/bash
WORKSPACE=$PWD/workspace
OUTPUTFILE=$WORKSPACE/"vm.output"
> $OUTPUTFILE
PYTHONADD="$1"
for PYTHONNAME in "${PYTHONADD[@]}"; do
    export PYTHONPATH=$PYTHONPATH:$PWD/$PYTHONNAME
done
# bash $WORKSPACE/bootupconfig.sh
jupyter lab \
  --no-browser --allow-root --port=8888 --ip='0.0.0.0' \
  --preferred-dir=$WORKSPACE \
  --FileContentsManager.delete_to_trash=False \
  --ServerApp.disable_check_xsrf=True \
  &> $OUTPUTFILE
