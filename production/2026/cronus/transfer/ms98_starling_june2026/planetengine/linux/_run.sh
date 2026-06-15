# #!/bin/bash
# DIR=$(dirname "$(readlink -f "$0")")
# MOUNTFROM=$(dirname "$DIR")/
# CAMPAIGNDIR=$(basename "$DIR")/
# MOUNTTO='/workspace/mount'
# SCRIPT='run.py'
# IMAGE='rsbyrne/planetengine:latest'
# INTERPRETER='python'
# LOGSDIR=$MOUNTFROM
# JOBNAME="test"
# OUTFILE=$LOGSDIR"/"$JOBNAME".out"
# ERRORFILE=$LOGSDIR"/"$JOBNAME".error"
# touch $OUTFILE
# touch $ERRORFILE
# docker run -v $MOUNTFROM:$MOUNTTO $IMAGE $INTERPRETER $MOUNTTO$CAMPAIGNDIR$SCRIPT "$@" > $OUTFILE 2> $ERRORFILE &
