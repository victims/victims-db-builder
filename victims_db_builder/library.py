import itertools
import httplib, string
import urllib2
import re
from decimal import *
import sys
from version import Version

class BaseLibrary(object):
    def __init__(self, versionRanges):
        #For soup/direct maven index:
        self.versions = []
        if not isinstance(versionRanges, basestring):
            for vr in versionRanges:
                self.versions.append(Version(vr))
        else:
            self.versions.append(Version(versionRanges))

        #for Maven central
        self.versionRanges = versionRanges
        self.fixVersionRange()
        #TODO push out to config
        self.maxRange = 99

    def splitRange(self, numRange):
        tmpVers = []
        if(',' in numRange):
            tmpVers =  string.split(numRange, ',')
        else:
            tmpBase = self.retlowHigh(numRange)
            tmpVers.append(numRange)
            tmpVers.append(tmpBase[0])
        return tmpVers

    # Assumes string "4.0.2"
    # Returns list of [4.0,2] for looping as float
    def retlowHigh(self, string):
        valList = []
        k = string.rfind(".")
        valList.append(string[:k])
        valList.append(string[k+1:])
        return valList

    ## Turn version into list, without beginning symbols
    def genVerString(self, version):
        numRangeArray = self.splitRange(version[2:])
        toScale = numRangeArray[0].count('.')
        fromScale = numRangeArray[1].count('.')
        fromValue = numRangeArray[1]
        while fromScale < toScale:
            fromValue += '.0'
            fromScale = fromValue.count('.')
            numRangeArray[1] = fromValue
        return numRangeArray

    # Remove duplicates and merge ranges in the version listing
    def fixVersionRange(self):
        tmpVerRanges = []
        if (len(self.versionRanges) > 1):
            for a, b in itertools.combinations(self.versionRanges,2):
                AListSplit = self.genVerString(a)
                AList = string.split(AListSplit[0], '.')
                BListSplit = self.genVerString(b)
                BList = string.split(BListSplit[0], '.')
                if len(BList) != 3 or len(AList) != 3:
                    #give up trying to fix version ranges
                    return
                AX = AList[0]; AY=AList[1]; AZ=AList[2]
                BX = BList[0]; BY=BList[1]; BZ=BList[2]

                if ((AX != BX) or (AY != BY)):
                    if(not a in tmpVerRanges): tmpVerRanges.append(a)
                    if(not b in tmpVerRanges): tmpVerRanges.append(b)
                else:
                    if(a[0] == b[0]):
                        # if the same symbol for the same X.Y version,
                        # assume last entry is correct
                        # switch out old for new version
                        if(not b in tmpVerRanges): tmpVerRanges.append(b)
                    else:
                        # symbols are different, need to combine two versions
                        if(a[0] == '<' and  b[0] == '>'):
                            if(AZ < BZ):
                                if(not a in tmpVerRanges): tmpVerRanges.append(a)
                                if(not b in tmpVerRanges): tmpVerRanges.append(b)
                            else:
                                tmpVersion = '<=' + str(AListSplit[0]) + ',' + BListSplit[0]
                                tmpVerRanges.append(tmpVersion)
                        else:
                            if(AZ > BZ):
                                if(not a in tmpVerRanges): tmpVerRanges.append(a)
                                if(not b in tmpVerRanges): tmpVerRanges.append(b)
                            else:
                                tmpVersion = '<=' + str(BListSplit[0]) + ',' + AListSplit[0]
                                tmpVerRanges.append(tmpVersion)
            self.versionRanges = tmpVerRanges
import re
import logging
import ConfigParser
from bs4 import BeautifulSoup
from os import environ
class JavaLibrary(BaseLibrary):
    def __init__(self, versionRange, groupId, artifactId):
        getcontext().prec = 2
        self.logger = logging.getLogger(__name__)
        super(JavaLibrary, self).__init__(versionRange)
        self.groupId = groupId
        self.artifactId = artifactId
        self.mavenVersions = set()
        self.configure()

    def configure(self):
        config = ConfigParser.ConfigParser()
        config.read('victims-db-builder.cfg')
        repos = config.items('java_repos')
        print "repos: %s" % repos
        for repo, url in repos:
            try:
                self.logger.debug('repo: %s' % repo)
                if repo == 'central':
                    self.logger.debug('setting index to %s' % url)
                    self.indexBaseUrl = url
                    self.anchor = config.get('java', 'anchor', 1,
                        {'groupId': self.groupId, 'artifactId' : self.artifactId})
                    self.confirmCentralVersions()
                    self.indexBaseUrl = config.get('java', 'download_base_url')
                    self.confirmVersions()
                else:
                    self.indexBaseUrl = url
                    self.confirmVersions()
            except:
                self.logger.warn('Processing of repo %s, skipping.' % repo)
                continue

    def confirmCentralVersions(self):
        coords = self.indexBaseUrl + self.groupId + "/" + self.artifactId
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

        #TODO cache page locally for redundency
        HTMLPage = response.read()

        for r in self.versionRanges:
            listString = self.genVerString(r)
            self.logger.debug('listString %s', listString)

            try:
                #split out values, for ['9.2.8', '9.2.0']
                valList= self.retlowHigh(listString[0])
                firstY = Decimal(valList[0])
                firstZ = int(valList[1])
                valList= self.retlowHigh(listString[1])
                secondY = Decimal(valList[0])
                secondZ = int(valList[1])

                if (r[0] == '>'):
                    yMax = secondY + Decimal('0.' + str(self.maxRange))
                    self.sortedAddVer(HTMLPage, coords, yMax, secondZ, firstY, firstZ)
                elif (r[0] == '<'):
                    self.sortedAddVer(HTMLPage, coords, firstY, firstZ, secondY, secondZ)
                else:
                    self.sortedAddVer(HTMLPage, coords, firstY, firstZ, firstY, firstZ)
            except ValueError:
                self.logger.debug('Couldnt generate versions for range: %s' % r)


    def sortedAddVer(self, HTMLPage, coords, AY, AZ, BY, BZ):
        self.logger.debug('AY:%.2f, AZ:%d, BY:%.2f, BZ:%d', AY, AZ, BY, BZ)
        ver = BY
        while ver >= BY and ver <= AY:
            if (ver == BY and ver == AY):
                for i in range (BZ,AZ+1):
                    self.addVer(ver, i, HTMLPage, coords)
            elif (ver == BY):
                for i in range (BZ, self.maxRange):
                    self.addVer(ver, i, HTMLPage, coords)
            elif (ver == AY):
                self.logger.debug('Matched ver to AY: %d == %d' % (ver, AY))
                for i in range(AZ+1):
                    self.addVer(ver, i, HTMLPage, coords)
            else:
                self.logger.debug('Didnt matched ver to AY: %d != %d' % (ver, AY))
                for i in range(self.maxRange):
                    self.addVer(ver, i, HTMLPage, coords)
            ver = ver + Decimal(0.1)

    def addVer(self, ver, i, HTMLPage, coords):
        tmpVers = str(ver) + "." + str(i)
        tmpAnchor = self.anchor + tmpVers
        results = self.regex_search(tmpVers, HTMLPage)
        if len(results) > 0:
            for (fullVer) in results:
                self.mavenVersions.add(fullVer)
        else:
           self.logger.debug(tmpAnchor + " not found on " + coords)

    def regex_search(self, tmpVers, target):
        self.logger.debug('tmpVers: %s', tmpVers)
        searchString = self.artifactId + '/' + tmpVers
        searchString = searchString.replace('.', '\\.')
        searchString += '([^"/]+)?'
        self.logger.debug('search with regex: %s', searchString)
        uniqueResults = set()
        for result in re.findall(searchString, target):
            self.logger.debug('result: %s', result)
            uniqueResults.add("%s%s" % (tmpVers, result))
        return uniqueResults

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
            if version.condition == '==':
                self.version.debug('condition was ==')
                self.version.debug('version is %s' % version)
            elif version.condition == '<=':
                self.logger.debug('condition was <=')
                startLinkIndex = links.index(findByRegex(version.series, soup))
                endLinkIndex = links.index(findByRegexReverse(version.base, soup))
                affectedLinks = links[startLinkIndex:endLinkIndex + 1]
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
