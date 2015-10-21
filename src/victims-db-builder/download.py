from vulnerability import Vulnerability
import string
import requests
import os

#############################################################
## Download
############################################################
# http://central.maven.org/maven2/org/springframework/spring-web/4.2.0.RELEASE/spring-web-4.2.0.RELEASE.jar

class MavenDownloader:
    downloadBaseUrl = "http://central.maven.org/maven2/"
    downloadDir = 'downloads/'

    listVer = []

    def __init__(self, libraries):
        self.libraries = libraries

    def parseGroupId(self, groupId):
        return string.replace(groupId, '.', '/')

    def parseVersionString(self, library, versionString):
        return '%s-%s' % (library.artifactId, versionString)

    def buildUrl(self, library, versionString):
        jarName = self.parseVersionString(library, versionString) + '.jar'
        #http://central.maven.org/maven2/org/springframework/3.2.2.RELEASE/3.2.2.RELEASE.jar
        url = '%s%s/%s/%s/%s' % (self.downloadBaseUrl, self.parseGroupId(library.groupId),
            library.artifactId, versionString, jarName)
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
        handle.close()
        if os.stat(filename) == 0:
            os.remove(filename)
            print "Cleaned up empty file: %s" % filename


    def prepare_request(self, library, version):
        jarUrl, jarName = self.buildUrl(library, version)
        localPath = self.downloadDir + jarName
        if not os.path.isfile(localPath):
            print "Downloading: %s to %s." % (jarUrl, localPath)
            self.dorequest(localPath, jarUrl)
            return localPath
        else:
            print "%s exists. Submitting anyway." % localPath
            return localPath

    ##http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
    ##############################################################
    ## Parse and build
    ##############################################################
    def download(self):
        newfiles = []
        for library in self.libraries:
            if library.versionRanges:
               for version in library.mavenCentralVersions:
                    print 'version: %s' % version
                    newLocalPath = self.prepare_request(library, version)
                    if newLocalPath is not None:
                        newfiles.append((newLocalPath, version,
                            library.groupId, library.artifactId))
            else:
                print "No libraries found"
        return newfiles

    ## Opens Maven file for product, and checks through the version range to see whether
    ## it is listed as a release on the page
    ## Checks page for ex.: "/artifact/org.springframework/spring-web/4.0.9.RELEASE"
    ## Example range: <=3.2.13,3.2
