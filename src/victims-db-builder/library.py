import itertools
import httplib, string
import urllib2
import re

class Library(object):
    def __init__(self, versionRanges):
        self.versionRanges = versionRanges
        self.fixVersionRange()
        ## upper range of z maintenance release
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

class JavaLibrary(Library):
    def __init__(self, versionRange, groupId, artifactId):
        super(JavaLibrary, self).__init__(versionRange)
        self.groupId = groupId
        self.artifactId = artifactId
        self.indexBaseUrl = "http://mvnrepository.com/artifact/"
        self.anchor = "/artifact/" + self.groupId + "/" + self.artifactId + "/"
        self.mavenCentralVersions = list()
        self.confirmVersions()

    def confirmVersions(self):
        coords = self.indexBaseUrl + self.groupId + "/" + self.artifactId
        print "coords %s" % coords
        try:
            response = urllib2.urlopen(coords)
        except urllib2.URLError, e:
            if not hasattr(e, "code"):
                raise
            response = e
            print "Error with MavenPage:", response.code, response.msg
            return []

        #TODO cache page locally for redundency
        HTMLPage = response.read()

        for r in self.versionRanges:
            listString = self.genVerString(r)
            print 'listString %s' % listString

            #split out values, for ['9.2.8', '9.2.0']
            valList= self.retlowHigh(listString[0])
            firstY = float(valList[0])
            firstZ = int(valList[1])
            valList= self.retlowHigh(listString[1])
            secondY = float(valList[0])
            secondZ = int(valList[1])

            if (r[0] == '>'):
                yMax = secondY + float('.' + str(self.maxRange))
                self.sortedAddVer(HTMLPage, coords, yMax, secondZ, firstY, firstZ)
            elif (r[0] == '<'):
                self.sortedAddVer(HTMLPage, coords, firstY, firstZ, secondY, secondZ)
            else:
                self.sortedAddVer(HTMLPage, coords, firstY, firstZ, firstY, firstZ)

        return self.mavenCentralVersions

    def sortedAddVer(self, HTMLPage, coords, AY, AZ, BY, BZ):
        print 'AY:%.2f, AZ:%d, BY:%.1f, BZ:%d' % (AY,AZ,BY,BZ)
        ver = BY
        while ver >= BY and ver <= AY:
            if (ver == BY and ver == AY):
                for i in range (BZ,AZ+1):
                    self.addVer(ver, i, HTMLPage, coords)
            elif (ver == BY):
                for i in range (BZ, self.maxRange):
                    self.addVer(ver, i, HTMLPage, coords)
            elif (ver == AY):
                for i in range(AZ+1):
                    self.addVer(ver, i, HTMLPage, coords)
            else:
                for i in range(self.maxRange):
                    self.addVer(ver, i, HTMLPage, coords)
            ver += 0.1

    def addVer(self, ver, i, HTMLPage, coords):
        tmpVers = str(ver) + "." + str(i)
        tmpAnchor = self.anchor + tmpVers
        results = self.regex_search(tmpVers, HTMLPage)
        if len(results) > 0:
            for (fullVer) in results:
                self.mavenCentralVersions.append(fullVer)
        else:
           print tmpAnchor + " not find on " + coords

    def regex_search(self, tmpVers, target):
        print 'tmpVers: %s' % tmpVers
        searchString = self.artifactId + '/' + tmpVers
        searchString = searchString.replace('.', '\\.')
        searchString += '([^"/]+)?'
        print 'search with regex: %s' % searchString
        uniqueResults = set()
        for result in re.findall(searchString, target):
            print 'result: %s' % result
            uniqueResults.add("%s%s" % (tmpVers, result))
        return uniqueResults
