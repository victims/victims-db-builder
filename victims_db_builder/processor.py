from download import MavenDownloader
from vulnerability import Vulnerability
import upload
from os import walk, path
from sys import argv
import logging
import logging.config

logging.config.fileConfig('logging.cfg')
logger = logging.getLogger('victimsDBBuilder')

def main(argv):
    if len(argv) != 4:
        print """Usage: python processor.py <dir|file.yaml>
            <victims-api-username> <victims-api-password>"""
    else:
        script, target, username, password = argv
        if target.endswith('.yaml'):
            processReport(target, username, password)
        else:
            findYamlFiles(target, username, password)


def findYamlFiles(baseDir, username, password):
    for root, dirs, files in walk(baseDir):
        for file in files:
            if file.endswith('.yaml'):
                yamlFile = path.join(root, file)
                logger.info("processing: %s", yamlFile)
                processReport(yamlFile, username, password)

def processReport(yamlFile, username, password):
    vuln = Vulnerability(yamlFile)
    downloader = MavenDownloader(vuln.libraries)
    newFileList = downloader.download()
    logger.info('newFileList: %s' % newFileList)
    for (newFile, version, groupId, artifactId) in newFileList:
        upload.uploadArchive(username, password, newFile, groupId, artifactId,
            version, vuln.cve)

if __name__ == '__main__':
    main(argv)
