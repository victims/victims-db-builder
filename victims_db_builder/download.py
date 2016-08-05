from vulnerability import Vulnerability
import string
import requests
import os
import logging
import ConfigParser

#############################################################
## Download
############################################################

class MavenDownloader:
    def __init__(self, libraries):
        self.logger = logging.getLogger(__name__)
        self.libraries = libraries
        config = ConfigParser.SafeConfigParser()
        config.read('victims-db-builder.cfg')
        #TODO change to index url
        self.downloadBaseUrl = config.get('java', 'index')
        self.downloadDir = config.get('java', 'download_dir')

    def parseGroupId(self, groupId):
        return string.replace(groupId, '.', '/')

    def parseVersionString(self, library, versionString):
        return '%s-%s' % (library.artifactId, versionString)

    def buildUrl(self, library, versionString):
        jarName = self.parseVersionString(library, versionString) + '.jar'
        url = '%s%s/%s/%s/%s' % (self.downloadBaseUrl, self.parseGroupId(library.groupId),
            library.artifactId, versionString, jarName)
        return (url, jarName)

    def dorequest(self, filename, url):
        with open(filename, 'wb') as handle:
            response = requests.get(url, stream="True")
            if not response.ok:
                self.logger.warning("Request to download %s failed. %s: %s",
                    url, response.status_code, response.text)
            else:
                for block in response.iter_content(1024):
                    handle.write(block)
        handle.close()
        if os.stat(filename) == 0:
            os.remove(filename)
            self.logger.debug("Cleaned up empty file: %s", filename)


    def prepare_request(self, library, version):
        jarUrl, jarName = self.buildUrl(library, version)
        localPath = self.downloadDir + jarName
        if not os.path.isfile(localPath):
            self.logger.info("Downloading: %s to %s.", jarUrl, localPath)
            self.dorequest(localPath, jarUrl)
            return localPath
        else:
            self.logger.warning("%s exists. Submitting anyway.", localPath)
            return localPath

    def download(self):
        newfiles = []
        for library in self.libraries:
            if library.versionRanges:
               for version in library.mavenCentralVersions:
                    self.logger.debug('version: %s', version)
                    newLocalPath = self.prepare_request(library, version)
                    if newLocalPath is not None:
                        newfiles.append((newLocalPath, version,
                            library.groupId, library.artifactId))
            else:
                self.logger.warning("No libraries found")
        return newfiles
