import vulnerability
import string
import requests
from os import path

#############################################################
## Download
############################################################
# http://central.maven.org/maven2/org/springframework/spring-web/4.2.0.RELEASE/spring-web-4.2.0.RELEASE.jar
indexBaseUrl = "http://central.maven.org:8080/maven2/"
downloadDir = 'downloads/'

def parseGroupId(groupId):
    return string.replace(groupId, '.', '/')

def parseVersionString(versionString):
    return string.replace(versionString, '/', '-')

def buildUrl(groupId, versionString):
    jarName = parseVersionString(versionString) + '.jar'
    url = '%s%s/%s/%s' % (indexBaseUrl, parseGroupId(groupId),
        versionString, jarName)
    return (url, jarName)

##http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
##############################################################
## Parse and build
##############################################################

def download(yamlFile):
    jars = vulnerability.Vulnerability(yamlFile)
    #jars.print_flaw()
    listVers = jars.checkMvnVer()
    if listVers:
       	for v in listVers:
            jarUrl, jarName = buildUrl(jars.groupId, v)
            localPath = downloadDir + jarName
            if not path.isfile(localPath):
                print "Downloading: %s to %s." % (jarUrl, localPath)
            else:
                print "%s exists." % localPath

download('3192.yaml')
