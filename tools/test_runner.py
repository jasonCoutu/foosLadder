"""Module to identify all unit tests that need to run and return a TestSuite object to be run"""

import os
import sys
import unittest
import logging
import re
import teamcity
from teamcity.unittestpy import TeamcityTestRunner

pt = os.getcwd()
root_dir = pt

loglevel = int(os.environ.get('UNITTEST_LOGLEVEL', logging.CRITICAL))
logging.getLogger().setLevel(loglevel) # DEBUG, LOG, WARN, ERROR(?) are too chatty

TEST_MODULES = [
    'test'
]

COVERAGE_OMIT_PATHS = [
    'test/*',
    'testotw/*'
    'src/lib/*',
    'src/app/models/backup.py',
    'tools/*',
    '/usr/local/google_appengine/*' ,
    'C:\Program Files (x86)\Google\google_appengine/*',
    '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/*',
    'src/app/views/jinja_ext/*',
    'src/app/views/__init__.py*',
    'src/app/views/account.py',
    'src/app/views/admin.py',
    'src/app/views/articles.py',
    'src/app/views/base.py',
    'src/app/views/customer_service.py',
    'src/app/views/errors.py',
    'src/app/views/f*.py',
    'src/app/views/googleplus.py',
    'src/app/views/l*.py',
    'src/app/views/meta.py',
    'src/app/views/otw_handlers/*',
    'src/app/views/root.py',
    'src/app/views/s*.py',
    'src/app/views/twitter.py'
]

def convert_module_path(module):
    """Helper method to convert a module in dot notation to
    a proper file path"""
    path_bits = module.split(".")
    return os.path.sep.join(path_bits)

def suite(test_re=None):
    """Iterate across all of the modules in TEST_MODULES, find all of the
    tests within and return a TestSuite which will run them all"""
    try:
        test_suite = unittest.TestSuite()

        if test_re:
            TEST_RE = test_re
        else:
            TEST_RE = r"^.*_tests?\.py$"

        # Search through every file inside this package.
        test_names = []

        for module in TEST_MODULES:
            test_dir = os.path.join(root_dir, convert_module_path(module))

            for filename in os.listdir(test_dir):

                if os.path.isdir(os.path.join(test_dir, filename)) and not filename.startswith("."):
                    TEST_MODULES.append(module + "." + filename)
                    continue

                if not re.match(TEST_RE, filename):
                    continue

                # Import the test file and find all TestClass clases inside it.
                module_name = '%s.%s' % (module, filename[:-3])
                test_module = __import__(module_name, {}, {}, filename[:-3])
                test_suite.addTest(unittest.TestLoader().loadTestsFromModule(test_module))

        return test_suite

    except Exception:
        logging.critical("Error loading tests.", exc_info=1)
        raise SystemExit("Error loading tests.")

if __name__ == "__main__":

    coverage_report_dir = os.environ.get('CODE_COVERAGE_DIR')
    
    if coverage_report_dir:
        from coverage import coverage
        cov = coverage(omit=COVERAGE_OMIT_PATHS, source=['app'])
        cov.start() # need to do this as early as possible to "catch" the import statements

    if len(sys.argv) == 2 and sys.argv[1] == 'testotw': # execute otw tests
            TEST_MODULES = ['testotw']
            test_suite = suite(r"^.*_otwtests?\.py$")
    elif len(sys.argv) == 3 and (sys.argv[1] == 'testotw' or sys.argv[2] == 'testotw'): # execute specified otw tests
        if sys.argv[1] == 'testotw':
            index = 2
        else:
            index = 1
        TEST_MODULES = ['testotw']
        name = str(sys.argv[index])
        name = name.replace('#', '.')   # Allows you to run test cases with the format testFile.testClass#testCase
        test_suite = unittest.TestLoader().loadTestsFromNames([name])
    elif len(sys.argv) > 1:    # execute only specified tests
        test_suite = unittest.TestLoader().loadTestsFromNames(sys.argv[1:])
    else:
        test_suite = suite()
    if teamcity.underTeamcity():
        TeamcityTestRunner().run(test_suite)
    else:
        unittest.TextTestRunner(verbosity=int(os.environ.get('UNITTEST_VERBOSITY', 1))).run(test_suite)

    if coverage_report_dir:
        cov.stop()
        cov.html_report(directory=coverage_report_dir)
        cov.erase()
