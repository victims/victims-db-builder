import yaml, httplib, string

class Vulnerability():

    def __init__(self, cve, title, description, cvss_v2, references, affected):
        self.cve = cve
	self.title = title
	self.description = description
	self.cvss_v2 = cvss_v2
	self.references = references
	self.affected = affected


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
#}i

#VERSION_REGEX = regex_compile(
#    r'^(?P<condition>[><=]=)'
#    r'(?P<version>[^, ]+)'
#    r'(?:,(?P<series>[^, ]+)){0,1}$'
#)


def parseYaml(document):
	stream = file(document)
	data = yaml.load(stream)
	return data['affected']

#http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
def genVersions(jars):
	for j in jars:
		ranges = j['version']
		for r in ranges:
			yield r

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

jars = parseYaml("../victims-cve-db/database/java/2015/3192.yaml")
ranges = genVersions(jars)
for r in ranges:
	genVersion(r)
