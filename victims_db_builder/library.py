import re
import string
import urllib2
from version import Version

class BaseLibrary(object):
    def __init__(self, versionRanges):
        self.versions = []
        if not isinstance(versionRanges, basestring):
            for vr in versionRanges:
                self.versions.append(Version(vr))
        else:
            self.versions.append(Version(versionRanges))


import logging
import ConfigParser
from bs4 import BeautifulSoup
class JavaLibrary(BaseLibrary):
    def __init__(self, versionRange, groupId, artifactId):
        self.logger = logging.getLogger(__name__)
        super(JavaLibrary, self).__init__(versionRange)
        self.groupId = groupId
        self.artifactId = artifactId
        self.configure()
        self.mavenVersions = set()
        self.confirmVersions()

    def configure(self):
        config = ConfigParser.ConfigParser()
        config.read('victims-db-builder.cfg')
        self.indexBaseUrl = config.get('java', 'index')

    def confirmVersions(self):
        coords = self.indexBaseUrl + self.groupId.replace('.', '/') + "/" + self.artifactId
        self.logger.debug("coords %s", coords)
        try:
            response = urllib2.urlopen(coords)
        except urllib2.URLError, e:
            if not hasattr(e, "code"):
                raise
            response = e
            self.logger.error("Response code:%s, Error with MavenPage: %s", response.code,
                response.msg)
            return []

        self.findInMaven(response)

    def findInMaven(self, response):
            #TODO cache page locally for redundency
            mavenPage = response.read()

            soup = BeautifulSoup(mavenPage, 'html.parser')

            for version in self.versions:
                self.logger.debug('version.base: %s' % version.base)
                versionRegex = re.compile(version.base.replace('.', '\.'))
                anchor = soup.find(href=versionRegex)
                if anchor:
                    self.logger.debug("adding %s to versions" % anchor.get_text().rstrip('/'))
                    self.mavenVersions.add(anchor.get_text().rstrip('/'))
                    self.findAllInSeries(anchor)
                else:
                    self.logger.warn('Didnt find %s' % version.base)

    #anchorRegex = re.compile(('?:[\d.]*(?=\.))(?P<postfix>.*)?')
    def findAllInSeries(self, baseAnchor):
        decimalCount = self.decimalCount(baseAnchor.get_text())
        for version in self.versions:
            if(version.condition == '>='):
                for anchor in baseAnchor.find_next_siblings("a"):
                    if version.series is not None:
                        seriesRegex = re.compile('^' + version.series)
                        if seriesRegex.match(anchor.get_text()):
                            self.mavenVersions.add(anchor.get_text().rstrip('/'))

    def decimalCount(self, version):
        return version.count('.')