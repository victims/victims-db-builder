# victims-db-builder

Parses CVE files from github.com/victims/victims-cve-db
and fills out package_urls for use by the victims process.

## Development
This is a short guide on how to work with this codebase

### Requirements

* python 3.x
* virtualenv
* pip

#### Setup the development environment

Create a virtualenv using:
```sh
virtualenv dbuild
```
You should see the following output, and a new folder 'dbbuild' should be created.
```sh
New python executable in dbbuild/bin/python3.5
Also creating executable in dbbuild/bin/python
Installing setuptools, pip, wheel...done.
```

#### Activate the development environment

Activate the previously created environment using:
```sh
source dbuild/bin/activate
```
Once this is complete, you should see the name prepended to the command prompt eg: '(dbbuild)'

#### Install the required dependencies

Install dependencies using 'pip':
```sh
 pip install -r requirements.txt
```

Add package_urls to a single entry:
```sh
 python victims_db_builder/processor.py ../tests/data/7501.yaml
```

#### Run the test suite

Install test dependencies using pip
```sh
  pip install -r test-requirements.txt
```

Use 'nose' to execute the test suite, found in the 'tests' directory using:
```sh
nosetests
```

Output will look like this for a successful run of the tests:
```sh
............
----------------------------------------------------------------------
Ran 12 tests in 16.545s

OK
```

#### Create a source distribution

Using distutil to create a '.tar' source distribution of the project:
```sh
python setup.py sdist
```

After running this, you should have a '.tar' file in 'dist/'
