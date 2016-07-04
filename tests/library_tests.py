import nose.tools
import yaml
from victims_db_builder.library import BaseLibrary, JavaLibrary

def test_multi_libraries():
    data = yaml.load(file('tests/data/6504.yaml'))
    libraries = data['affected']
    loaded_libraries = []
    for affectedLibrary in libraries:
        version = affectedLibrary['version']
        artifactId = affectedLibrary['artifactId']
        groupId = affectedLibrary['groupId']
        lib = JavaLibrary(version, groupId, artifactId)
        assert len(lib.versions) >= 1
        loaded_libraries.append(lib)
    assert len(loaded_libraries) == 4

def test_down_series_3():
    lib = JavaLibrary(['<=9.2.8,9.2'], "org.eclipse.jetty","jetty-http")
    assert checkEquals(lib.mavenVersions, ["9.2.0.M0", "9.2.0.M1", "9.2.0.RC0",
        "9.2.0.v20140526","9.2.1.v20140609", "9.2.2.v20140723", "9.2.2.v20140723",
        "9.2.3.v20140905","9.2.4.v20141103","9.2.5.v20141112/","9.2.6.v20141205",
        "9.2.7.v20150116")

def test_up_series_3():
    lib = JavaLibrary(['>=9.2.3,9.2'], "org.eclipse.jetty","jetty-http")
    assert checkEquals(lib.mavenVersions, ["9.2.3.v20140905","9.2.4.v20141103",
        "9.2.5.v20141112", "9.2.6.v20141205", "9.2.7.v20150116", "9.2.8.v20150217", "9.2.9.v20150224"])

def test_fix_version_y_only():
    lib = BaseLibrary([">=0.5,0"])
    assert lib.versions[0].base == '0.5'

def test_no_series():
    lib = BaseLibrary([">=4.6.3", ">=2.5"])
    assert lib.versions[0].base == '4.6.3'
    assert lib.versions[1].base == '2.5'

def test_letter_in_range():
    lib = BaseLibrary(['<=3.11-beta1,3.11'])
    assert lib.versions[0].base == '3.11-beta1'
    assert lib.versions[0].series == '3.11'

def test_regex_with_appendix():
    lib = JavaLibrary(['3.2.13,3.2', '4.1.6,4'], "org.springframework",
        "spring-web")
    searchString = open('tests/data/spring-web.html').read()
    matchResult = lib.regex_search('4.2.0', searchString)
    (ref) = matchResult.pop()
    #print "ref: %s" % ref
    #self.assertIsNotNone(appendix)
    assert '4.2.0.RELEASE' == ref

def test_generate_down_from_x():
    lib = JavaLibrary([">=1.7.0,1"], "org.codehaus.groovy", "groovy-all")
    assert len(lib.mavenVersions) == 36

def test_generate_up_from_x():
    lib = JavaLibrary(["<=2.4.3,2"], "org.codehaus.groovy", "groovy-all")
    #TODO this might change if another release of groovy in the 2 range is released
    assert len(lib.mavenVersions) == 57


def checkEquals(S1,S2):
    print sorted(S1)
    return len(S1) == len(S2) and sorted(S1) == sorted(S2)
