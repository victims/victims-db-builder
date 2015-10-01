from sys import argv
from os import path
from download import download as mvnDownload

def checkFileExists(filename):
    if path.isfile(filename):
        return True
    else:
        return False

def process(yamlFile):
    mvnDownload(yamlFile)

if len(argv) == 1:
    print "No input file specified."
else:
    yamlFile = argv[1]
    if(checkFileExists(yamlFile)):
        process(yamlFile)
    else:
        print yamlFile + " does not exist"
