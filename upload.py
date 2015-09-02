import requests, string, base64

filename="/Users/jasonshepherd/Downloads/spring-web-4.2.0.RELEASE.jar"
hostname="localhost"
port=5000
username="jshepher"
password="Welcome1!"

def upload(filename, version, groupId, artifactId, cves):
	file = open(filename)
	files = { 'file': file } 
	print "uploading file: " + filename
        server = "http://{0}:{1}".format(hostname, port)
        url = "{0}/service/submit/archive/java/?version={1}&groupId={2}&artifactId={3}&cves={4}".format(server, version, groupId, artifactId, cves)
	print url 
	response = requests.put(url, files, auth=(username, password))
	print response

#import urllib2, base64

#request = urllib2.Request(URL)
#base64string = base64.encodestring('%s:%s' % (KEY, PASSWORD)).replace('\n', '')
#request.add_header("Authorization", "Basic %s" % base64string)   
#result = urllib2.urlopen(request)

upload(filename,"4.2.0", "org.springframework", "spring-web", "CVE-2013-0000")
