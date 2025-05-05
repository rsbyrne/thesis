DIR="$(dirname "$0")"
for var in 0 1 2 3 4 5 6 7 8 9 10 11
do
  sh $DIR/runseries.sh $* $var &
done
