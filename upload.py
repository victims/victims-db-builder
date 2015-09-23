import requests, string, base64, hash

filename="/Users/jasonshepherd/Downloads/spring-web-4.2.0.RELEASE.jar"
hostname="localhost"
port=5000
username="jshepher"
password="Welcome1!"

def uploadArchive(filename, cves):
	archive = open(filename)
	#files = { 'file': file }
	#print "uploading file: " + filename
	server = "http://{0}:{1}".format(hostname, port)
	url = "{0}/service/v2/submit/archive/java/?cves={1}".format(server, cves)
	print "url:" + url
	response = requests.put(url,
		data={
			'archive' : archive
		},
		auth=(username, password))
	print response

def uploadHash(filename):
	fullHash = hash.doHash(filename)
	coordinates = {
		'groupId':'org.springframework',
		'artifactId':'spring-web',
		'version':'4.2.0'
	}
	#print coordinates

	requestDict = {
		'entry':fullHash,
		'cves': ['CVE-2015-0000'],
		'coordinates':coordinates
	}

	#print requestDict

#import urllib2, base64

#request = urllib2.Request(URL)
#base64string = base64.encodestring('%s:%s' % (KEY, PASSWORD)).replace('\n', '')
#request.add_header("Authorization", "Basic %s" % base64string)
#result = urllib2.urlopen(request)

uploadArchive(filename, "CVE-2013-0000")

#uploadHash(filename)
