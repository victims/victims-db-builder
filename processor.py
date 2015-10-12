from download import MavenDownloader
import upload

def processReport(yamlFile):
    downloader = MavenDownloader(yamlFile)
    vuln = downloader.vulnerability
    newFileList = downloader.download()
    print 'newFileList: %s' % newFileList
    for (newFile, versionId) in newFileList:
        upload.uploadArchive(newFile, vuln.groupId, vuln.artifactId,
            versionId, vuln.cve)

processReport('3192.yaml')
