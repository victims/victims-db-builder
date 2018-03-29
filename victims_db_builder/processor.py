import os
import vulnerability
import upload
from os import walk, path
from sys import argv
import logging
import logging.config

logging.config.fileConfig('logging.cfg')
logger = logging.getLogger('victimsDBBuilder')

def main(argv):
    if len(argv) != 2:
        print("Usage: python processor.py <dir|file.yaml>")
        raise SystemExit(1)
    else:
        script, target = argv
        if target.endswith('.yaml'):
            processReport(target)
        else:
            findYamlFiles(target)

def findYamlFiles(baseDir):
    for root, dirs, files in walk(baseDir):
        for file in files:
            if file.endswith('.yaml'):
                yamlFile = path.join(root, file)
                logger.info("processing: %s", yamlFile)
                processReport(yamlFile)

def processReport(yamlFile):
    vuln = vulnerability.construct_yaml(yamlFile)
    if vuln.package_urls is not None:
        print('package_urls is already defined in {}'.format(yamlFile))
        raise SystemExit(2)

    vuln.add_libraries()
    with open(yamlFile, 'a') as yf:
        yf.write('package_urls:\n')
        for library in vuln.libraries:
            groupId = library.groupId
            artifactId = library.artifactId
            yf.write('    - {}\n'.format(library.url))


if __name__ == '__main__':
    main(argv)
