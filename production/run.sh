INTERPRETER=python3
DATE=$(date +%s)
oldIFS="$IFS"
IFS="-"
OUTFILE="$*""."$DATE".out"
ERRORFILE="$*""."$DATE".error"
IFS=$oldIFS
$INTERPRETER $* 1> $OUTFILE 2> $ERRORFILE &