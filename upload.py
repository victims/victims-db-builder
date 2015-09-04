import requests, string, base64, json, hash
from hashlib import md5, sha512
from datetime import datetime
from hmac import HMAC

filename="spring-web-4.2.0.RELEASE.jar"
hostname="localhost"
port=5000
server = "http://{0}:{1}".format(hostname, port)
username="jshepher"
password="Welcome1!"
apikey='61BB27B1438204C5E3BB03C65BAEA85'
secretKey='2E0369DD5929ED42897BCBE67E9048639457617E'
VICTIMS_API_HEADER = 'X-Victims-Api'
content_type = 'application/json'

def uploadArchive(filename, version, groupId, artifactId, cves):
	file = open(filename)
	files = { 'file': file }
	print "uploading file: " + filename
        server = "http://{0}:{1}".format(hostname, port)
        url = "{0}/service/submit/archive/java/?version={1}&groupId={2}&artifactId={3}&cves={4}".format(server, version, groupId, artifactId, cves)
	print url
	response = requests.put(url, files, auth=(username, password))
	print response

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


def createSubmission(filename):
	hashes = hash.doHash(filename)
	#coordinates = {
	#	'groupId':'org.springframework',
	#	'artifactId':'spring-web',
	#	'version':'4.2.0'
	#}
	#print coordinates

	hashes[ 'name'] ='someVuln'
	hashes['cves'] = ['CVE-2015-0000']

	return json.dumps(hashes)

def json_submit(path, data, md5sums, apikey, secret):
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'Date': date,'Content-Type':content_type}
        url = server + path
        if apikey is not None and secret is not None:
            signature = generate_signature(secret, 'PUT', path, date, md5sums, )
            headers[VICTIMS_API_HEADER]= 'apikey' + ':' + 'signature'
        return requests.put(
            url, headers=headers,
            data=data,
        )

#import urllib2, base64

#request = urllib2.Request(URL)
#base64string = base64.encodestring('%s:%s' % (KEY, PASSWORD)).replace('\n', '')
#request.add_header("Authorization", "Basic %s" % base64string)
#result = urllib2.urlopen(request)

#upload(filename,"4.2.0", "org.springframework", "spring-web", "CVE-2013-0000")




data = createSubmission(filename)
md5sums = [md5(data).hexdigest()]
path = '/service/v2/submit/hash/java/'
print json_submit(path, data, md5sums, apikey, secretKey)
