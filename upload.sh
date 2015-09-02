#!/bin/bash
export APIKEY=CD95C4729A3CB524E40EDFCBF09CE7A0
export SIGNATURE=B88550215317E561809843D21FB9D5534D527661
export ARCHIVE='cassandra-all-2.1.3.jar'
export VICTIMS_SERVER='localhost:5000'
export VID=2.1.3
export AID=cassandra-all
export GID=org.apache.cassandra
export CVE_REF=CVE-2015-0225
export USERNAME=jasinner
export PASSWORD='Welcome1!'
export SECRET='B88550215317E561809843D21FB9D5534D527661'
export METHOD=PUT
export PATH="/service/submit/archive/java/?version=$VID&groupId=$GID&artifactId=$AID&cves=$CVE_REF"
export DATE="Thu, 19 Aug 2015 06:33:37 GMT"
export MD5="dc8704e367d9ab9a50cc8fff6367b537"


#<dependency>
#	<groupId>org.apache.cassandra</groupId>
#	<artifactId>cassandra-all</artifactId>
#	<version>2.1.3</version>
#</dependency>

curl -v -u $USERNAME:$PASSWORD -X PUT -F archive=@$ARCHIVE http://$VICTIMS_SERVER/service/submit/archive/java/?version=$VID\&groupId=$GID\&artifactId=$AID\&cves=$CVE_REF

#*   Trying 127.0.0.1...
#* Connected to localhost (127.0.0.1) port 5000 (#0)
#* Server auth using Basic with user 'jasinner'
#> PUT /service/submit/archive/java/?version=2.1.3&groupId=org.apache.cassandra&artifactId=cassandra-all&cves=CVE-2015-0225 HTTP/1.1
#> Host: localhost:5000
#> Authorization: Basic amFzaW5uZXI6V2VsY29tZTEh
#> User-Agent: curl/7.43.0
#> Accept: */*
#> Content-Length: 4199396
#> Expect: 100-continue
#> Content-Type: multipart/form-data; boundary=------------------------2f70a2c63ed93d60
#>
#< HTTP/1.1 100 Continue
#* HTTP 1.0, assume close after body
#< HTTP/1.0 201 CREATED
#< Content-Type: application/json
#< Content-Length: 36
#< Server: Werkzeug/0.10.4 Python/2.7.10
#< Date: Wed, 19 Aug 2015 05:40:47 GMT
#<
#* Closing connection 0

#echo "PATH: $PATH"
#curl -v -X $METHOD -H "X-Victims-Api: $APIKEY:$SIGNATURE" -H "Date: Thu, 22 Aug 2013 15:20:37 GMT" -F archive=@$ARCHIVE http://$VICTIMS_SERVER/service/submit/archive/java/?version=$VID\&groupId=$GID\&artifactId=$AID\&cves=$CVE_REF

#* Send failure: Broken pipe
#* Closing connection 0
#curl: (55) Send failure: Broken pipe
#Jasons-MacBook-Pro:victims-db-builder jasonshepherd$ ./upload.sh
#*   Trying 127.0.0.1...
#* Connected to localhost (127.0.0.1) port 5000 (#0)
#> PUT /service/submit/archive/java/?version=VID&groupId=GID&artifactId=AID&cves=CVE-2013-0000,CVE-2013-0001 HTTP/1.1
#> Host: localhost:5000
#> User-Agent: curl/7.43.0
#> Accept: */*
#> X-Victims-Api: CD95C4729A3CB524E40EDFCBF09CE7A0:B88550215317E561809843D21FB9D5534D527661
#> Date: Thu, 22 Aug 2013 15:20:37 GMT
#> Content-Length: 4199396
#> Expect: 100-continue
#> Content-Type: multipart/form-data; boundary=------------------------59d0df63ac1260d4
#>
#< HTTP/1.1 100 Continue
#* HTTP 1.0, assume close after body
#< HTTP/1.0 403 FORBIDDEN
#< Content-Type: application/json
#< Content-Length: 9
#< Server: Werkzeug/0.10.4 Python/2.7.10
#< Date: Wed, 19 Aug 2015 05:34:21 GMT
