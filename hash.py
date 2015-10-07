from victims_hash.fingerprint import fingerprint
from sys import argv

def doHash(filename):
    return fingerprint(filename)

filename = argv[1]
print doHash(filename)
