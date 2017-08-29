import itertools
import string
import urllib2
from decimal import *
from distutils.version import LooseVersion

from version import Version


class BaseLibrary(object):
    def __init__(self, versionRanges):
        # For soup/direct maven index:
        self.versions = []
        if not isinstance(versionRanges, basestring):
            for vr in versionRanges:
                self.versions.append(Version(vr))
        else:
            self.versions.append(Version(versionRanges))

        # for Maven central
        self.versionRanges = versionRanges
        self.fixVersionRange()
        # TODO push out to config
        self.maxRange = 99

    def splitRange(self, numRange):
        tmpVers = []
        if ',' in numRange:
            tmpVers = string.split(numRange, ',')
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
        valList.append(string[k + 1:])
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
            for a, b in itertools.combinations(self.versionRanges, 2):
                AListSplit = self.genVerString(a)
                AList = string.split(AListSplit[0], '.')
                BListSplit = self.genVerString(b)
                BList = string.split(BListSplit[0], '.')
                if len(BList) != 3 or len(AList) != 3:
                    # give up trying to fix version ranges
                    return
                AX = AList[0]
                AY = AList[1]
                AZ = AList[2]
                BX = BList[0]
                BY = BList[1]
                BZ = BList[2]

                if ((AX != BX) or (AY != BY)):
                    if (not a in tmpVerRanges): tmpVerRanges.append(a)
                    if (not b in tmpVerRanges): tmpVerRanges.append(b)
                else:
                    if (a[0] == b[0]):
                        # if the same symbol for the same X.Y version,
                        # assume last entry is correct
                        # switch out old for new version
                        if (not b in tmpVerRanges): tmpVerRanges.append(b)
                    else:
                        # symbols are different, need to combine two versions
                        if (a[0] == '<' and b[0] == '>'):
                            if (AZ < BZ):
                                if (not a in tmpVerRanges): tmpVerRanges.append(a)
                                if (not b in tmpVerRanges): tmpVerRanges.append(b)
                            else:
                                tmpVersion = '<=' + str(AListSplit[0]) + ',' + BListSplit[0]
                                tmpVerRanges.append(tmpVersion)
                        else:
                            if (AZ > BZ):
                                if (not a in tmpVerRanges): tmpVerRanges.append(a)
                                if (not b in tmpVerRanges): tmpVerRanges.append(b)
                            else:
                                tmpVersion = '<=' + str(BListSplit[0]) + ',' + AListSplit[0]
                                tmpVerRanges.append(tmpVersion)
                                # self.versionRanges = tmpVerRanges


import re
import logging
import ConfigParser
from bs4 import BeautifulSoup


class JavaLibrary(BaseLibrary):
    def __init__(self, versionRange, groupId, artifactId):
        getcontext().prec = 2
        self.logger = logging.getLogger(__name__)
        super(JavaLibrary, self).__init__(versionRange)
        self.groupId = groupId
        self.artifactId = artifactId
        self.mavenVersions = set()
        self.affectedMvnSeries = set()
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
                                             {'groupId': self.groupId, 'artifactId': self.artifactId})
                    # self.confirmCentralVersions()
                    self.indexBaseUrl = config.get('java', 'download_base_url')
                    self.confirmVersions()
                else:
                    self.indexBaseUrl = url
                    self.confirmVersions()
            except:
                self.logger.warn('Processing of repo %s, skipping.' % repo)
                continue
        self.findAllInSeries()

    def confirmVersions(self):
        coords = self.indexBaseUrl + self.groupId.replace('.', '/') + "/" + self.artifactId
        self.logger.debug("coords %s", coords)
        try:
            response = urllib2.urlopen(coords)
        except urllib2.URLError, e:
            if response.code is 404:
                pass
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
                # The last anchor found
                return links.pop()

        # TODO cache page locally for redundency
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

    def findAllInSeries(self):
        verList = []
        regex = ['(,)(\\d+)(\\.)(\\d+)', '(,)(\\d+)']
        for val in self.versionRanges:
            # removing the boundary version if exists
            normalized = None
            boundary = None
            for ind, value in enumerate(regex):
                res = re.compile(value)
                matched = res.search(val)
                if matched is not None and ind == 0:
                    normalized = val.replace(
                        str(matched.group(1) + matched.group(2) + matched.group(3) + matched.group(4)), '')
                    tmp = str(matched.group(1) + matched.group(2) + matched.group(3) + matched.group(4))
                    boundary = tmp.replace(',', '')
                    break
                if matched is not None and ind == 1:
                    normalized = val.replace(str(matched.group(1) + matched.group(2)), '')
                    tmp = str(matched.group(1) + matched.group(2))
                    boundary = tmp.replace(',', '')
                    break
                else:
                    normalized = val

            if '>=' in normalized:
                verList.append(StructureHelper('>=', normalized.replace('>=', ''), boundary))
            if '<=' in normalized:
                verList.append(StructureHelper('<=', normalized.replace('<=', ''), boundary))
            if '<' in normalized and '=' not in normalized:
                verList.append(StructureHelper('<', normalized.replace('<', ''), boundary))
            if '>' in normalized and '=' not in normalized:
                verList.append(StructureHelper('>', normalized.replace('>', ''), boundary))
            if '==' in normalized:
                verList.append(StructureHelper('==', normalized.replace('==', ''), boundary))

        equalsFound = set()
        links = []
        self.findEqualVersions(verList, 0, equalsFound, links)

        finalVersionRanges = []
        if len(links) != 0:
            for each in links:
                versionRange = []
                for ea in each.links:
                    originalVerListValue = verList[ea]
                    versionRange.append(originalVerListValue.symbol + originalVerListValue.version)
                    versionRange.append(originalVerListValue.boundary)
                versionRange.append(each.symbol + each.version)
                finalVersionRanges.append(EqualBaseVersion(versionRange))
        else:
            versionRange = []
            for each in verList:
                versionRange.append(each.symbol + each.version)
                versionRange.append(each.boundary)
                finalVersionRanges.append(EqualBaseVersion(versionRange))

        self.findAllArtifacts(finalVersionRanges)

    # Building the relationship between affected versions in case any version
    # lives between two other versions without
    def findEqualVersions(self, ver, inx, equalsList, links):
        indx = inx
        highIndex = len(ver) - 1
        equalVer = ver[indx]

        try:
            if indx >= highIndex:
                return equalsList
            for index, var in enumerate(ver):
                if index <= highIndex and index is indx:
                    continue
                if isinstance(var, StructureHelper) and isinstance(equalVer, StructureHelper):
                    # Striping the third precision to compare the base versions
                    if self.normalizeText(equalVer.version) == self.normalizeText(var.version):
                        if len(links) != 0:
                            for ix, value in enumerate(links):
                                if self.normalizeText(equalVer.version) == self.normalizeText(value.version):
                                    if not any(eq == indx for eq in value.links):
                                        structureObject = links[ix]
                                        if isinstance(structureObject, StructureHelper):
                                            structureObject.addToLinks(index)
                                elif ix == len(links) - 1:
                                    self.addStructureToLinks(equalVer, index, links)
                                else:
                                    continue
                        else:
                            self.addStructureToLinks(equalVer, index, links)

            self.findEqualVersions(ver, indx + 1, equalsList, links)
        except Exception as e:
            self.logger.error("Error occurred while building affected versions relationship", str(e))

    def addStructureToLinks(self, equalVer, index, links):
        if equalVer.symbol == '>=':
            c = StructureHelper('>=', equalVer.version, equalVer.boundary)
            c.addToLinks(index)
            links.append(c)
        if equalVer.symbol == '<=':
            c = StructureHelper('<=', equalVer.version, equalVer.boundary)
            c.addToLinks(index)
            links.append(c)
        if equalVer.symbol == '==':
            c = StructureHelper('==', equalVer.version, equalVer.boundary)
            c.addToLinks(index)
            links.append(c)
        if equalVer.symbol == '>':
            c = StructureHelper('>', equalVer.version, equalVer.boundary)
            c.addToLinks(index)
            links.append(c)
        if equalVer.symbol == '<':
            c = StructureHelper('<', equalVer.version, equalVer.boundary)
            c.addToLinks(index)
            links.append(c)

    def normalizeText(self, text):
        baseVersion = ''
        for indx, char in enumerate(text):
            if indx <= 2:
                baseVersion += str(char)
        return baseVersion

    def findAllArtifacts(self, translatedVersions):

        if len(self.mavenVersions) == 0:
            self.logger.warn('acquired maven artifacts is empty')

        if len(translatedVersions) != 0:
            for version in translatedVersions:
                for mvn in self.mavenVersions:
                    mavenSuffix = []
                    found = False
                    comparableVersion = ''
                    for char in mvn:
                        if found is not True:
                            if char == '.':
                                comparableVersion += char
                                continue
                            try:
                                integerChar = int(char)
                                comparableVersion += str(integerChar)
                            except ValueError:
                                mavenSuffix.append(char)
                                found = True
                        else:
                            mavenSuffix.append(char)
                    attachedSuffix = ''

                    for su in mavenSuffix:
                        attachedSuffix += str(su)

                    # Case where boundary version is specified as one digit i.e 9
                    if len(version.boundary) == 1 and version.boundary == comparableVersion[:1]:
                        self.compareVersions(attachedSuffix, comparableVersion, version)

                    # Case where boundary version is specified with decimal point i.e 9.2
                    if len(version.boundary) == 3 and version.boundary == self.normalizeText(comparableVersion):
                        # Case where affected versions are between to versions
                        if version.greaterThanOrEqualTo is not None and version.lessThanOrEqualTo is not None:
                            if (LooseVersion(comparableVersion) == LooseVersion(version.greaterThanOrEqualTo.replace('<=', '')) or
                                    (LooseVersion(comparableVersion) < LooseVersion(version.greaterThanOrEqualTo.replace('<=', ''))
                                     and LooseVersion(comparableVersion) > LooseVersion(version.lessThanOrEqualTo.replace('>=', '')))) and \
                                (LooseVersion(comparableVersion) == LooseVersion(version.lessThanOrEqualTo.replace('>=', '')) or
                                     (LooseVersion(comparableVersion) > LooseVersion(version.lessThanOrEqualTo.replace('>=', '')) and
                                      LooseVersion(comparableVersion) < LooseVersion(version.greaterThanOrEqualTo.replace('<=', '')))):
                                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)
                        self.compareVersions(attachedSuffix, comparableVersion, version)

        else:
            self.logger.warn('either affected version range is unavailable')

        print self.affectedMvnSeries

    def populatedAffectedLibraries(self, attachedSuffix, comparableVersion):
        self.affectedMvnSeries.add(
            AffectedJavaLibrary(self.groupId, self.artifactId, str(comparableVersion + attachedSuffix)))

    def compareVersions(self, attachedSuffix, comparableVersion, version):
        if version.equal is not None:
            if LooseVersion(version.equal.replace('==', '')) == LooseVersion(comparableVersion):
                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)
        if version.greaterThanOrEqualTo is not None and version.lessThanOrEqualTo is None:
            if LooseVersion(comparableVersion) == LooseVersion(version.greaterThanOrEqualTo.replace('<=', '')) or \
                            LooseVersion(comparableVersion) < LooseVersion(
                        version.greaterThanOrEqualTo.replace('<=', '')):
                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)
        if version.lessThanOrEqualTo is not None and version.greaterThanOrEqualTo is None:
            if LooseVersion(comparableVersion) == LooseVersion(version.lessThanOrEqualTo.replace('>=', '')) or \
                            LooseVersion(comparableVersion) > LooseVersion(version.lessThanOrEqualTo.replace('>=', '')):
                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)
        if version.greaterThan is not None:
            if LooseVersion(comparableVersion) < LooseVersion(version.greaterThan.replace('<', '')):
                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)
        if version.lessThan is not None:
            if LooseVersion(comparableVersion) > LooseVersion(version.lessThan.replace('>', '')):
                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)

        # Case where an affected version is between two other versions
        if version.lessThan is not None and version.greaterThan is not None:
            if LooseVersion(comparableVersion) < LooseVersion(version.greaterThan.replace('<', '')) and \
                            LooseVersion(comparableVersion) > LooseVersion(version.lessThan.replace('>', '')):
                self.populatedAffectedLibraries(attachedSuffix, comparableVersion)


class AffectedJavaLibrary:
    def __init__(self, groupId, artifactId, version):
        self.groupId = groupId
        self.artifactId = artifactId
        self.version = version


class EqualBaseVersion:
    def __init__(self, *args):
        self.equal = None
        self.lessThanOrEqualTo = None
        self.greaterThanOrEqualTo = None
        self.lessThan = None
        self.greaterThan = None
        self.boundary = None

        for arg in args:
            for each in arg:
                if '==' in each:
                    self.equal = each
                elif '>=' in each:
                    self.lessThanOrEqualTo = each
                elif '<=' in each:
                    self.greaterThanOrEqualTo = each
                elif '>' in each and '=' not in each:
                    self.lessThan = each
                elif '<' in each and '=' not in each:
                    self.greaterThan = each
                else:
                    self.boundary = each


class StructureHelper:
    def __init__(self, symbol, version, boundary):
        self.symbol = symbol
        self.version = version
        self.boundary = boundary
        self.links = set()

    def addToLinks(self, link):
        self.links.add(link)