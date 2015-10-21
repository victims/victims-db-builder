from download import MavenDownloader
from vulnerability import Vulnerability
import upload
from os import walk, path
from sys import argv

def findYamlFiles(baseDir):
    for root, dirs, files in walk(baseDir):
        for file in files:
            if file.endswith('.yaml'):
                yamlFile = path.join(root, file)
                print "processing: %s" % yamlFile
                processReport(yamlFile)

def processReport(yamlFile):
    vuln = Vulnerability(yamlFile)
    downloader = MavenDownloader(vuln.libraries)
    newFileList = downloader.download()
    print 'newFileList: %s' % newFileList
    for (newFile, version, groupId, artifactId) in newFileList:
        upload.uploadArchive(newFile, groupId, artifactId,
            version, vuln.cve)

if len(argv) != 2:
    print "Usage: python processor.py <dir>|<file.yaml>"
else:
    script, target = argv
    if target.endswith('.yaml'):
        processReport(target)
    else:
        findYamlFiles(target)
