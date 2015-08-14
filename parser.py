import yaml, httplib

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
#}

def parseYaml(document):
	stream = file(document)
	data = yaml.load(stream)
	return data

#http://central.maven.org/maven2/org/springframework/spring-web/4.1.6.RELEASE/spring-web-4.1.6.RELEASE.jar
def getArtifact(data):
	page = httplib.HTTPConnection("central.maven.org")
	groupId = data.affected.groupId.replace('.', '/')
	page.request("GET", "maven2/" + groupId + data.affected.artifactId)
	response = page.getresponse()
	print response

data = parseYaml("../victims-cve-db/database/java/2015/3192.yaml")
getArtifact(data)
