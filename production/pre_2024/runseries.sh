DIR="$(dirname "$0")"
for var in 0 1 2 3 4 5
do
  DATE=$(date +%s)
  oldIFS="$IFS"
  IFS="-"
  OUTFILE=$DIR/"runa.sh"."$*""-"$var"."$DATE".out"
  ERRORFILE=$DIR/"runa.sh"."$*""-"$var"."$DATE".error"
  sh $DIR/runa.sh $* $var 1> $OUTFILE 2> $ERRORFILE
done
