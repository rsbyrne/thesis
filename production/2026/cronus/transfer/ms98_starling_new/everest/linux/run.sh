SCRIPT=$1
N=$2
BASENAME=$(basename "$SCRIPT")
LOGSDIR="./logs"
rm -rf $LOGSDIR
mkdir -p $LOGSDIR
INTERPRETER=python3
for i in $(seq 1 $N)
do
  OUTFILE=$LOGSDIR"/"$BASENAME"_"$i".out"
  ERRORFILE=$LOGSDIR"/"$BASENAME"_"$i".error"
  $INTERPRETER -u $SCRIPT 1> $OUTFILE 2> $ERRORFILE &
done
