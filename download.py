from vulnerability import Vulnerability
import string
import requests
from os import path

#############################################################
## Download
############################################################
# http://central.maven.org/maven2/org/springframework/spring-web/4.2.0.RELEASE/spring-web-4.2.0.RELEASE.jar

class MavenDownloader:
    indexBaseUrl = "http://central.maven.org/maven2/"
    downloadDir = 'downloads/'

    def __init__(self, document):
        self.vulnerability = Vulnerability(document)

    def parseGroupId(self, groupId):
        return string.replace(groupId, '.', '/')

    def parseVersionString(self, versionString):
        return string.replace(versionString, '/', '-')

    def buildUrl(self, groupId, versionString):
        jarName = self.parseVersionString(versionString) + '.jar'
        url = '%s%s/%s/%s' % (self.indexBaseUrl, self.parseGroupId(groupId),
            versionString, jarName)
        return (url, jarName)

    def dorequest(self, filename, url):
        with open(filename, 'wb') as handle:
            response = requests.get(url, stream="True")
            if not response.ok:
                print "Request to download %s failed. %s: %s" % (
                    url, response.status_code, response.text)
            else:
                for block in response.iter_content(1024):
                    handle.write(block)

    def prepare_request(self, groupId, version):
        jarUrl, jarName = self.buildUrl(groupId, version)
        localPath = self.downloadDir + jarName
        if not path.isfile(localPath):
            print "Downloading: %s to %s." % (jarUrl, localPath)
            self.dorequest(localPath, jarUrl)
            return localPath
        else:
            print "%s exists." % localPath
            return None

    ##http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
    ##############################################################
    ## Parse and build
    ##############################################################
    def download(self):
        newfiles = []
        listVers = self.vulnerability.checkMvnVer()
        if listVers:
       	    for v in listVers:
                newLocalPath = self.prepare_request(self.vulnerability.groupId, v)
                if newLocalPath is not None:
                    newfiles.append((newLocalPath, v))
        return newfiles
