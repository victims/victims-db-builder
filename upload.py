import requests
from hmac import HMAC
from datetime import datetime
from hashlib import md5, sha512

hostname="localhost"
port=5000
server = "http://{0}:{1}".format(hostname, port)
username="jshepher"
password="Welcome1!"


def uploadArchive(filename, gid, aid, vid, cves):
    print "uploading file: " + filename
    server = "http://%s:%s" % (hostname, port)
    path = "/service/v2/submit/archive/java/?version=%s\&groupId=%s\&artifactId=%s\&cves=%s" % (
        vid, gid, aid, ','.join(cves))
    url = server + path
    #date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    with open(filename, 'rb') as archive:
        #md5sums = [md5(archive.read()).hexdigest()]
        #archive.seek(0)
        files = { 'archive': archive }
        response = requests.put(url,
            #headers = {'X-Victims-Api': "%s:%s" % (apiKey, generate_signature(
            #	secret, 'PUT', path, date, md5sums)),
            #	"Date": date},
            files=files,
            auth = (username, password)
            )
    print response.text

