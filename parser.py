import yaml, httplib, string
import urllib
import urllib2

#COMMON_FIELDS = {
#    'cve': FieldValidator([is_string, is_cve]),
#    'title': FieldValidator([is_string]),
#    'description': FieldValidator([is_text], False),
#    'cvss_v2': FieldValidator([is_cvss_v2], False),
#    'references': FieldValidator([is_references], False),
#    'affected': FieldValidator([is_affected])
#}

#LANGUAGE_FIELDS = {
#    'python': {
#        'name': FieldValidator([is_string]),
#        'version': FieldValidator([is_version]),
#        'fixedin': FieldValidator([is_version], False),
#        'unaffected': FieldValidator([is_version], False),
#    },
#    'java': {
#        'groupId': FieldValidator([is_string]),
#        'artifactId': FieldValidator([is_string]),
#        'version': FieldValidator([is_version]),
#        'fixedin': FieldValidator([is_version], False),
#        'unaffected': FieldValidator([is_version], False),
#    }
#}

#VERSION_REGEX = regex_compile(
#    r'^(?P<condition>[><=]=)'
#    r'(?P<version>[^, ]+)'
#    r'(?:,(?P<series>[^, ]+)){0,1}$'
#)

##############################################################
## Parsing variables and functions
##############################################################

mvnRoot="http://mvnrepository.com/artifact/"
## upper range of z maintenance release in maven page, just a guess
maxRange = 30

def genVersions(jars):
	for j in jars:
		ranges = j['version']
		for r in ranges:
			yield r

#http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
def genVersion(version):
	if version[0] == '>':
		genDown(splitRange(version[2:]))
	elif version[0] == '<':
		genUp(splitRange(version[2:]))
	else:
		pass
#TODO test singe version and validate
#		yield version[1:]

def splitRange(numRange):
	return string.split(numRange, ',')

def genUp(numRangeArray):
	toScale = numRangeArray[0].count('.')
	fromScale = numRangeArray[1].count('.')
	fromValue = numRangeArray[1]
	while fromScale < toScale:
		fromValue += '.0'
		fromScale = fromValue.count('.')
	numRangeArray[1] = fromValue
	print numRangeArray

def genDown(numRangeArray):
    pass

def genVerString(version):
    numRangeArray = splitRange(version[2:])
    toScale = numRangeArray[0].count('.')
    fromScale = numRangeArray[1].count('.')
    fromValue = numRangeArray[1]
    while fromScale < toScale:
    	fromValue += '.0'
        fromScale = fromValue.count('.')
    numRangeArray[1] = fromValue
    return numRangeArray

# Assumes string "4.0.2"
# Returns list of [4.0,2] for looping as float
def retlowHigh(string):
	valList = []
	k = string.rfind(".")
	valList.append(string[:k])
	valList.append(string[k+1:])
	return valList

##############################################################
## Vulnerability class
## Used for both parsing yaml file and building individual jar files
##############################################################

class Vulnerability():
	
    def __init__(self, cve, title, description, cvss_v2, references, affected):
        self.cve = cve
	self.title = title
	self.description = description
	self.cvss_v2 = cvss_v2
	self.references = references
	self.affected = affected

    ## For loading in Yaml info
    def __init__(self,document):
	data = yaml.load(file(document))
        self.cve = data['cve']
        self.title = data['title']
        self.description = data['description']
        self.cvss_v2 = data['cvss_v2']
        self.references = data['references']
        self.affected = data['affected']	
	for j in self.affected:
		self.groupId = j['groupId']
		self.artifactId = j['artifactId']
		self.verRanges = j['version']
    
    ## Prints out basics
    def print_flaw(self):
	print "CVE= " + self.cve
        print "groupId= " + self.groupId
	print "artifactId= " + self.artifactId
	for r in self.verRanges:
        	genVersion(r)

## Opens Maven file for product, and checks through the version range to see whether
## it is listed as a release on the page
## Checks page for ex.: "/artifact/org.springframework/spring-web/4.0.9.RELEASE"
## Example range: <=3.2.13,3.2

    def checkMvnVer(self):
	listVer = []
	mvnFile = mvnRoot + self.groupId + "/" + self.artifactId
	## test file: mvnFile = mvnRoot + "/sillness"
	try:
 		response = urllib2.urlopen(mvnFile)
	except urllib2.URLError, e:
		if not hasattr(e, "code"):
			raise
		response = e
		print "Error with MavenPage:", response.code, response.msg
		return [] 

	HTMLPage = response.read()
              
        anchor = "/artifact/" + self.groupId + "/" + self.artifactId + "/"
	
	for r in self.verRanges:
		listString = genVerString(r)
		
		#split out values
		valList=retlowHigh(listString[1])
		lowDown = float(valList[0])
		lowUp = int(valList[1])
		valList=retlowHigh(listString[0])
		highDown = float(valList[0])
		highUp = int(valList[1])
		
        	ver = lowDown
        	while ver >= lowDown and ver <= highDown:
	                if (ver == lowDown and ver == highDown):
			  	for i in range (lowUp,highUp+1):	
					tmpVers = str(ver) + "." + str(i)
					tmpAnchor = anchor + tmpVers + ".RELEASE"
					if tmpAnchor in HTMLPage:
                        			listVer.append(tmpVers)
			elif (ver == lowDown):
				for i in range (lowUp,maxRange):
					tmpVers = str(ver) + "." + str(i)
					tmpAnchor = anchor + tmpVers + ".RELEASE"
					if tmpAnchor in HTMLPage:
                        			listVer.append(tmpVers)
			elif (ver == highDown):
				for i in range(highUp+1):
					tmpVers = str(ver) + "." + str(i)
					tmpAnchor = anchor + tmpVers + ".RELEASE"
					if tmpAnchor in HTMLPage:
                        			listVer.append(tmpVers)
			else:
				for i in range(maxRange):
					tmpVers = str(ver) + "." + str(i)
					tmpAnchor = anchor + tmpVers + ".RELEASE"
					if tmpAnchor in HTMLPage:
        					listVer.append(tmpVers)
                	ver += 0.1
	return listVer 
	

##http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
##############################################################
## Parse and build
##############################################################

jars = Vulnerability("../victims-cve-db/database/java/2015/3192.yaml")
jars.print_flaw()
listVers = jars.checkMvnVer() 
#if listVers:
#	print "Found releases in page:"
#	for v in listVers:
#		print v
