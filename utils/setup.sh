echo "Setting up Enviroment"

sudo apt update

sudo apt install -y mongodb

sudo apt install python3-pip

pip3 install pymango

sudo systemctl status mongod

mongo --eval 'db.runCommand({ connectionStatus: 1 })'

mongo

show dbs

use mongodb

show collections

exit

python3 load_balancer.py 20
gzip logfile.xml into logfile.xml.gz
