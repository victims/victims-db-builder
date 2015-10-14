from vulnerability import Vulnerability
import string
import requests
from os import path

#############################################################
## Download
############################################################
# http://central.maven.org/maven2/org/springframework/spring-web/4.2.0.RELEASE/spring-web-4.2.0.RELEASE.jar

class MavenDownloader:
    dwnloadBaseUrl = "http://central.maven.org/maven2/"
    downloadDir = 'downloads/'

    listVer = []

    def __init__(self, document):
        self.libraries = Vulnerability(document).libraries

    def parseGroupId(self, groupId):
        return string.replace(groupId, '.', '/')

    def parseVersionString(self, versionString, library):
        return '%s-%s' % (library.artifactId, versionString)

    def buildUrl(self, groupId, versionString):
        jarName = self.parseVersionString(versionString) + '.jar'
        #http://central.maven.org/maven2/org/springframework/3.2.2.RELEASE/3.2.2.RELEASE.jar
        url = '%s%s/%s/%s/%s' % (self.indexBaseUrl, self.parseGroupId(groupId),
            self.vulnerability.artifactId, versionString, jarName)
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
        for library in self.libraries:
            listVers = self.checkMvnVer()
            if listVers:
       	        for v in listVers:
                    print 'version: %s' % v
                    newLocalPath = self.prepare_request(self.vulnerability.groupId, v)
                    if newLocalPath is not None:
                        newfiles.append((newLocalPath, v))
        return newfiles

    ## Opens Maven file for product, and checks through the version range to see whether
    ## it is listed as a release on the page
    ## Checks page for ex.: "/artifact/org.springframework/spring-web/4.0.9.RELEASE"
    ## Example range: <=3.2.13,3.2
