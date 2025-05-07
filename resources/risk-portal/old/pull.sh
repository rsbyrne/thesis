#!/bin/bash
CREDENTIALS=` cat .credentials.txt `
SCRIPT='./../fbapi/fb_pull.sh'
URLROOT='https://www.facebook.com/geoinsights-portal/downloads/?id='
cat fbids.txt | while read line
do
sudo chmod -R 777 *
$SCRIPT $URLROOT$line $CREDENTIALS $PWD'/data/'$line
sudo chmod -R 777 *
done