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
        #TODO for each index page in indexBaseUrl list
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

        def getVersionRegex(target):
            return re.compile('^' + target.replace('.', '\.'))

        def findByRegex(target, soup):
            self.logger.debug('target: %s' % target)
            targetRegex = getVersionRegex(target)
            self.logger.debug('using regex %s' % targetRegex.pattern)
            link = soup.find('a', text=targetRegex)
            if link:
                self.logger.debug('found link: %s' % link)
                return link
            else:
                self.logger.warn('target \'%s\' not found' % target)

        def findByRegexReverse(target, soup):
            self.logger.debug('target reverse: %s' % target)
            targetRegex = getVersionRegex(target)
            self.logger.debug('using regex %s' % targetRegex.pattern)
            links = soup.find_all('a', text=targetRegex)
            if links is None or len(links) == 0:
                self.logger.warn('target \'%s\' not found' % target)
            else:
                #The last anchor found
                return links.pop()


        #TODO cache page locally for redundency
        mavenPage = response.read()
        soup = BeautifulSoup(mavenPage, 'html.parser')
        links = soup.find_all('a')

        for version in self.versions:
            if version.condition == '<=':
                self.logger.debug('condition was <=')
                startLinkIndex = links.index(findByRegex(version.series, soup))
                endLinkIndex = links.index(findByRegexReverse(version.base, soup))
                affectedLinks = links[startLinkIndex:endLinkIndex]
                self.logger.debug('%s affected links found' % len(affectedLinks))
                for affectedLink in affectedLinks:
                    self.mavenVersions.add(affectedLink.get_text().rstrip('/'))
            else:
                self.logger.warn('%s condition was not matched' % version.condition)

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
