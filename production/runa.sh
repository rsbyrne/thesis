DIR="$(dirname "$0")"
INTERPRETER=python3
DATE=$(date +%s)
oldIFS="$IFS"
IFS="-"
OUTFILE=$DIR/"$*""."$DATE".out"
ERRORFILE=$DIR/"$*""."$DATE".error"
IFS=$oldIFS
$INTERPRETER $DIR/$* 1> $OUTFILE 2> $ERRORFILE
