import vulnerability
import string
import urllib2

#############################################################
## Download
############################################################
# http://central.maven.org/maven2/org/springframework/spring-web/4.2.0.RELEASE/spring-web-4.2.0.RELEASE.jar
indexBaseUrl = "http://central.maven.org/maven2/"

def parseGroupId(groupId):
    return string.replace(groupId, '.', '/')

def buildUrl(groupId, artifactId, versionString):
    return '{0}{1}/{2}/{3}/{2}-{3}.jar'.format(indexBaseUrl, parseGroupId(groupId), artifactId, versionString)

##http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
##############################################################
## Parse and build
##############################################################

def download(yamlFile):
    jars = vulnerability.Vulnerability(yamlFile)
    jars.print_flaw()
    listVers = jars.checkMvnVer()
    if listVers:
       	for v in listVers:
	    jarUrl = buildUrl(jars.groupId, jars.artifactId, v)
            print "Downloading" + jarUrl
