* Configure the MongoDB yum repo:

```
sudo cat <<EOF > /etc/yum.repos.d/mongodb.repo
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/7.0/\$basearch/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-7.0.asc
EOF
```

* Install some dependencies and mongosh:

```
sudo dnf install rlwrap git podman buildah java-17-openjdk curl curl-devel gcc python3.11 python3.11-devel python3.11-pip mongodb-mongosh oracle-instantclient-release-el8
sudo dnf install oracle-instantclient-sqlplus oracle-instantclient-tools oracle-instantclient-basic

```

* Update pip:

```
sudo pip3.11 install --update pip
```

* Create a virtual environment for python:
```
python3 -m venv bands
source bands/bin/activate
```

* Install pip dependencies for the project:

```
cat > requirements.txt  <<EOF
oracledb
jupyterlab
pandas
ipython-sql
prettytable
pyvis
matplotlib
logging
wptools
mwparserfromhell
cx_Oracle
xmltodict
pymongo
EOF

pip install -r requirements.txt
```

* Install ORDS (you should setup the DB first):

```
wget https://download.oracle.com/otn_software/java/ords/ords-latest.zip
unzip -d ords ords-latest.zip && cd ords/bin

DBA_USERNAME=sys
HOST=bands0.dbbands
SERVICE=pbands_rw
echo WelcomeWelcome##123 > password.txt
echo WelcomeWelcome##123 >> password.txt

./ords install --admin-user $DBA_USERNAME --db-hostname $HOST --db-port 1521 --db-servicename $SERVICE --feature-sdw true --db-user ORDS_PUBLIC_USER --log-folder ../log  --password-stdin  <password.txt
```

* Enable the MongoDB API:
```
./ords config set mongo.enabled true
```

* Start ORDS:
```
~/ords/bin/ords --config ~/ords/bin serve &
```

* The output will show the MongoDB URL, note it down:
```
~/ords/bin/ords --config ~/ords/bin serve &
```

* Download and unzip SQLcl:
```
wget https://download.oracle.com/otn_software/java/sqldeveloper/sqlcl-latest.zip
unzip sqlcl-latest.zip
```

* Open the ports:

```
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=27017/tcp
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload
```

