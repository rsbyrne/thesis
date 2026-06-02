currentDir=$PWD
cd "$(dirname "$0")"
scp -r -v -o IPQoS="throughput" -i ~/.ssh/general.pem ./transfer/* ubuntu@172.26.131.135:~/volume/
