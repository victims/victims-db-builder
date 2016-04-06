from vulnerability import Vulnerability
import string
import requests
import os
import logging
import ConfigParser
import charon

#############################################################
## Download
############################################################

class MavenDownloader:
    def __init__(self, libraries):
        self.logger = logging.getLogger(__name__)
        self.libraries = libraries
        config = ConfigParser.SafeConfigParser()
        config.read('victims-db-builder.cfg')
        self.downloadDir = config.get('java', 'download_dir')

    def parseVersionString(self, library, versionString):
        return '%s-%s' % (library.artifactId, versionString)


    def prepare_request(self, library, version):
        jarName = self.parseVersionString(library, version) + '.jar'
        localPath = self.downloadDir + jarName
        if not os.path.isfile(localPath):
            self.logger.info("Downloading: %s to %s.", jarName, localPath)
            info = {'groupId': library.groupId, 'artifactId':library.artifactId, 'version':version}
            charon.download('java', info)
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
