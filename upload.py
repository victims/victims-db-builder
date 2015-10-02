import requests
from hmac import HMAC
from datetime import datetime
from hashlib import md5, sha512

filename="/Users/jasonshepherd/Downloads/spring-web-4.2.0.RELEASE.jar"
hostname="localhost"
port=5000
#secret = "CAB87262DF0B02D4C5D79D64B0E80D91A9539B24"
#apiKey = "00F25937A918DB067428B1CB5F5AC148"
username = 'jasinner'
password = 'Welcome1!'

def generate_signature(secret, method, path, date, md5sums):
    md5sums.sort()
    ordered = [method, path, date] + md5sums
    string = ''

    for content in ordered:
        if content is None:
            raise ValueError('Required header not found')
        string += str(content)

    return HMAC(
        key=bytes(secret),
        msg=string.lower(),
        digestmod=sha512
    ).hexdigest().upper()

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


uploadArchive(filename, 'org.springframework', 'spring-web', '4.2.0', ["CVE-2013-0007"])
