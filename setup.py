import os
import sys
from distutils.version import StrictVersion

from pip import __version__ as pip_version
from setuptools import find_packages, setup
from setuptools.version import __version__ as setuptools_version

python = sys.executable
if StrictVersion(setuptools_version) < StrictVersion("40.0"):
    emsg = "setuptools>=40 have to be installed"
    try:
        s = os.system('{} -m pip install "setuptools>=40"'.format(python))
    except Exception:
        raise Exception(emsg)
    else:
        if s != 0:
            raise Exception(emsg)
        os.execl(python, python, *sys.argv)

if StrictVersion(pip_version) < StrictVersion("20.0"):
    emsg = "pip>=20 have to be installed"
    try:
        s = os.system('{} -m pip install "pip>=20.0"'.format(python))
    except Exception:
        raise Exception(emsg)
    else:
        if s != 0:
            raise Exception(emsg)
        os.execl(python, python, *sys.argv)


with open(os.path.join("version.txt")) as version_file:
    version_from_file = version_file.read().strip()

with open("requirements.txt") as f_required:
    required = f_required.read().splitlines()

with open("test_requirements.txt") as f_tests:
    required_for_tests = f_tests.read().splitlines()

setup(
    name="cloudshell-networking-cisco",
    url="http://www.qualisystems.com/",
    author="QualiSystems",
    author_email="info@qualisystems.com",
    packages=find_packages(),
    install_requires=required,
    tests_require=required_for_tests,
    version=version_from_file,
    description="QualiSystems networking cisco specific package",
    include_package_data=True,
    python_requires=(
        ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, <4"
    ),
)
