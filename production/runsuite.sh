currentDir=$PWD
cd "$(dirname "$0")"
sh ex.sh sh workspace/runpara.sh $*
cd $currentDir