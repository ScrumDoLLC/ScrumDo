import os, sys
from setuptools import setup, find_packages
from pkg_resources import parse_requirements


version = 'master'


def read_requirements(path):
    """Reads requirement files
    """
    with open(os.path.join(*path)) as stream:
        for line in stream:
            if len(line.strip()) > 0 and not line.strip()[0] in ['#','-']:
                yield line.strip()


# pylint: disable-msg=W0102
def get_requirements(requirements_files, extras=[], remove=[]):
    """Generates the requirements.

    The major problem we have here is that requirements are contained in
    *multiple* requirement files, and some have even contradicting versions.

    What we do here, simply, is to chain the various requirements files (the
    ``requirements_files`` attribute, a list of paths to requirements files
    expressed as tuples of components) together, keeping a single entry for
    each package with the ones coming later overriding the first ones.

    The ``extras`` is a list of extra requirement to add and the ``remove``
    option is a list of keys (lowercase names of projects) not to install
    (despite being in some requirement files)
    """

    requirements_map = {}
    requirements = []
    for path in requirements_files:
        requirements.extend(read_requirements(path))
    requirements.extend(extras)
    for requirement in parse_requirements(requirements):
        if not requirement.key in remove:
            requirements_map[requirement.key] = requirement
    result = []
    for requirement in requirements_map.values():
        result.append(str(requirement))
    return result


removed_requires = ['pil', 'mysql-python', 'python-dateutil']
if sys.version_info > (2, 7):
    removed_requires.append('importlib')
install_requires = get_requirements(
    [
        ['Pinax-0.7.3-bundle', 'requirements', 'libs.txt'],
        ['Pinax-0.7.3-bundle', 'requirements', 'external_apps.txt'],
        ['requirements.txt']
    ],
    extras = [
        'django-timezones==0.2.dev1',
        'Django==1.1.4',
        'Pillow',
        'Pinax==0.7.3'
    ],
    remove = removed_requires
)


setup(
    name='ScrumDo',
    version=version,
    author="ScrumDo LLC",
    description="ScrumDo Agile Story Tracking Website",
    long_description=open('README.md').read(),
    license="GPL",
    keywords="",
    url='http://scrumdo.org',
    classifiers=[],
    packages=find_packages('scrumdo-web'),
    package_dir = { '': 'scrumdo-web' },
    include_package_data = True,
    install_requires = install_requires,
    zip_safe=False
)
