from download import MavenDownloader
import upload
from os import walk, path

def findYamlFiles(baseDir):
    for root, dirs, files in walk(baseDir):
        for file in files:
            if file.endswith('.yaml'):
                yamlFile = path.join(root, file)
                print "processing: %s" % yamlFile
                processReport(yamlFile)

def processReport(yamlFile):
    downloader = MavenDownloader(yamlFile)
    vuln = downloader.vulnerability
    newFileList = downloader.download()
    print 'newFileList: %s' % newFileList
    for (newFile, versionId) in newFileList:
        upload.uploadArchive(newFile, vuln.groupId, vuln.artifactId,
            versionId, vuln.cve)

findYamlFiles("/Users/jasonshepherd/projects/victims/victims-cve-db/database/java")
