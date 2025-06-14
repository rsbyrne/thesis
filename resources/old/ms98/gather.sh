#gather.sh

DIR="$(dirname "$0")"

#cp $DIR/../MS98kit/MS98.frm $DIR/miranda1.frm
#mv $DIR/../phd/pluto1_working/MS98kit/MS98.frm $DIR/pluto1old.frm
#mv $DIR/../phd/pluto2_working/MS98kit/MS98.frm $DIR/pluto2old.frm
#mv $DIR/../phd/pluto3_working/MS98kit/MS98.frm $DIR/pluto3old.frm
#mv $DIR/../phd/pluto4_working/MS98kit/MS98.frm $DIR/pluto4old.frm
#mv $DIR/../phd/pluto5_working/MS98kit/MS98.frm $DIR/pluto5old.frm
#mv $DIR/../phd/pluto6_working/MS98kit/MS98.frm $DIR/pluto6old.frm

scp -i ~/.ssh/general.pem ubuntu@45.113.235.136:~/pluto1_working/MS98kit/MS98.frm $DIR/pluto1.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.233.242:~/pluto2_working/MS98kit/MS98.frm $DIR/pluto2.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.233.237:~/pluto3_working/MS98kit/MS98.frm $DIR/pluto3.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.233.238:~/pluto4_working/MS98kit/MS98.frm $DIR/pluto4.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.186:~/pluto5_working/MS98kit/MS98.frm $DIR/pluto5.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.233.246:~/pluto6_working/MS98kit/MS98.frm $DIR/pluto6.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/MS98kit/MS98.frm $DIR/miranda1.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/cospar/pluto1old.frm $DIR/pluto1old.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/cospar/pluto2old.frm $DIR/pluto2old.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/cospar/pluto3old.frm $DIR/pluto3old.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/cospar/pluto4old.frm $DIR/pluto4old.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/cospar/pluto5old.frm $DIR/pluto5old.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.111:/work/volume/cospar/pluto6old.frm $DIR/pluto6old.frm
scp -i ~/.ssh/general.pem ubuntu@45.113.235.59:~/miranda2_working/MS98kit/MS98.frm $DIR/miranda2.frm
