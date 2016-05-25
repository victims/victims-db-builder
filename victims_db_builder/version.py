import re

class Version(object):
    def __init__(self, versionRange):
        prog = re.compile('^(?P<condition>[><=]=)(?P<version>[^, ]+)(?:,(?P<series>[^, ]+)){0,1}$')
        matchResult = prog.match(versionRange)
        assert matchResult
        self.base = matchResult.group('version')
        self.condition = matchResult.group('condition')
        self.series = matchResult.group('series')
