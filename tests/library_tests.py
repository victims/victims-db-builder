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
        try:
            lib = JavaLibrary(version, groupId, artifactId)
        except ValueError, e:
            print 'adding library %s/%s/%s' % (groupId, artifactId, version)
        else:
            loaded_libraries.append(lib)
    assert len(loaded_libraries) == 3

def test_fix_version():
    lib = BaseLibrary(['>=9.2.3,9.2', '<=9.2.8,9.2'])
    assert lib.versionRanges == ['<=9.2.8,9.2.3']

def test_fix_version_y_only():
    lib = BaseLibrary([">=0.5,0"])
    assert lib.versionRanges == ['>=0.5,0']

def test_no_series():
    lib = BaseLibrary([">=4.6.3", ">=2.5"])
    assert lib.versionRanges == ['>=4.6.3', '>=2.5']

def test_letter_in_range():
    lib = BaseLibrary(['<=3.11-beta1,3.11'])
    assert lib.versionRanges == ["<=3.11-beta1,3.11"]

def test_regex_with_appendix():
    lib = JavaLibrary(['3.2.13,3.2', '4.1.6,4'], "org.springframework",
        "spring-web")
    searchString = open('tests/data/spring-web.html').read()
    matchResult = lib.regex_search('4.2.0', searchString)
    (ref) = matchResult.pop()
    #print "ref: %s" % ref
    #self.assertIsNotNone(appendix)
    assert '4.2.0.RELEASE' == ref

def test_regex():
    lib = JavaLibrary(['>=9.2.3,9.2', '<=9.2.8,9.2'], "org.eclipse.jetty",
        "jetty-http")
    searchString = '''
<td><a href="jetty-http/9.2.0.v20140526" class="vbtn release">9.2.0.v20140526
</a></td><td><div><a href="jetty-http/9.2.0.v20140526/usages">6</a>
<span class="rb" style="width:7px;"></span></div></td><td>release</td><td>
(May, 2014)</td></tr><tr><td><a href="jetty-http/9.2.0.M1"
class="vbtn milestone">9.2.0.M1</a></td><td><div><a href="jetty-http/9.2.0.M1/
usages">6</a><span class="rb" style="width:7px;"></span></div></td>
<td>milestone</td><td> (May, 2014)</td></tr><tr><td>
<a href="jetty-http/9.2.0.M0" class="vbtn milestone">9.2.0.M0</a></td>
<td><div><a href="jetty-http/9.2.0.M0/usages">6</a>
<span class="rb" style="width:7px;"></span></div></td>'''
    matchResult = lib.regex_search('9.2.0', searchString)
    assert '9.2.0.v20140526' in matchResult
    assert '9.2.0.M1' in matchResult
    assert '9.2.0.M0' in matchResult

def test_generate_down_from_x():
    lib = JavaLibrary([">=1.7.0,1"], "org.codehaus.groovy", "groovy-all")
    assert len(lib.mavenCentralVersions) == 36

def test_generate_up_from_x():
    lib = JavaLibrary(["<=2.4.3,2"], "org.codehaus.groovy", "groovy-all")
    #TODO this might change if another release of groovy in the 2 range is released
    assert len(lib.mavenCentralVersions) == 57

def test_retLowHigh():
    lib = BaseLibrary([])
    assert lib.retlowHigh("1.0.0") ==  ['1.0', '0']
