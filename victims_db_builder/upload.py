import requests
from hmac import HMAC
from datetime import datetime
#from hashlib import md5, sha512
import logging
import logging.config
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('victims-db-builder.cfg')
hostname = config.get('victims_api', 'hostname')
port = config.get('victims_api', 'port')
protocol = config.get('victims_api', 'protocol')
server = "{0}://{1}:{2}".format(protocol, hostname, port)

logging.config.fileConfig('logging.cfg')
logger = logging.getLogger('victimsDBBuilder')

def uploadArchive(username, password, filename, gid, aid, vid, cves):
    logger.info("uploading file: " + filename)
    server = "%s://%s:%s" % (protocol, hostname, port)
    path = "/service/v2/submit/archive/java/?version=%s\&groupId=%s\&artifactId=%s\&cves=%s" % (
        vid, gid, aid, ','.join(cves))
    url = server + path
    #date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    with open(filename, 'rb') as archive:
        #md5sums = [md5(archive.read()).hexdigest()]
        #archive.seek(0)
        files = { 'archive': archive }
        response = requests.put(url,
            #headers = {'X-Victims-Api': "%s:%s" % (apiKey, generate_signature(
            #	secret, 'PUT', path, date, md5sums)),
            #	"Date": date},
            files=files,
            auth = (username, password),
	    verify='gd_bundle-g2.crt'
            )
    	logger.info(response.text)
