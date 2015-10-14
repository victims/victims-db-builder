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

    def test_multi_ver_ranges(self):
        data = yaml.load(file('test/2080.yaml'))
        libraryObjects = list()
        libraries = data['affected']
        for affectedLibrary in libraries:
            print affectedLibrary['version']

if __name__ == '__main__()':
    unittest.main()
