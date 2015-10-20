import unittest
import yaml
import library

class TestVulnerability(unittest.TestCase):
    def test_java_construct(self):
        data = yaml.load(file('test/3192.yaml'))
        libraryObjects = list()
        libraries = data['affected']
        for affectedLibrary in libraries:
            version = affectedLibrary['version']
            artifactId = affectedLibrary['artifactId']
            groupId = affectedLibrary['groupId']
            libraryObjects.append(library.JavaLibrary(version, groupId, artifactId))
        self.assertTrue(len(libraryObjects), 4)

    def test_multi_libraries(self):
        data = yaml.load(file('test/6504.yaml'))
        libraries = data['affected']
        for affectedLibrary in libraries:
            version = affectedLibrary['version']
            artifactId = affectedLibrary['artifactId']
            groupId = affectedLibrary['groupId']
            try:
                lib = library.JavaLibrary(version, groupId, artifactId)
            except ValueError, e:
                print e
            else:
                print lib.mavenCentralVersions

    def test_fix_version(self):
        lib = library.Library(['>=9.2.3,9.2', '<=9.2.8,9.2'])
        self.assertEquals(lib.versionRanges, ['<=9.2.8,9.2.3'])

    def test_fix_version_y_only(self):
        lib = library.Library([">=0.5,0"])
        self.assertEquals(lib.versionRanges, ['>=0.5,0'])

    def test_no_series(self):
        lib = library.Library([">=4.6.3", ">=2.5"])
        self.assertEquals(lib.versionRanges, ['>=4.6.3', '>=2.5'])

    def test_letter_in_range(self):
        lib = library.Library(['<=3.11-beta1,3.11'])
        self.assertEquals(lib.versionRanges, ["<=3.11-beta1,3.11"])

    def test_generate_down_from_x(self):
        lib = library.JavaLibrary([">=1.7.0,1"], "org.codehaus.groovy", "groovy-all")
        print lib.mavenCentralVersions

    def test_generate_up_from_x(self):
        lib = library.JavaLibrary(["<=2.4.3,2"], "org.codehaus.groovy", "groovy-all")
        print lib.mavenCentralVersions

    def test_retLowHigh(self):
        lib = library.Library([])
        print lib.retlowHigh("1.0.0")

if __name__ == '__main__()':
    unittest.main()
