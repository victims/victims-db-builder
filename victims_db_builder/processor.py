from download import MavenDownloader
import vulnerability
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
    vuln = vulnerability.construct_yaml(yamlFile)
    for library in vuln.libraries:
        groupId = library.groupId
        artifactId = library.artifactId
        for version in library.mavenCentralVersions:
            print "version %s" % version
            upload.submit(username, password, groupId, artifactId,
                version, vuln.cve)

if __name__ == '__main__':
    main(argv)
