echo "db.artist.insertOne({'link': 'The Mighty Mighty Bosstones', 'name': 'The Mighty Mighty Bosstones'})" | mongosh --tlsAllowInvalidCertificates "mongodb://bands:Bands%23%23123@localhost:27017/bands?authMechanism=PLAIN&authSource=\$external&ssl=true&retryWrites=false&loadBalanced=true"
