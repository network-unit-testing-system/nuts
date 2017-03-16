from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nuts',
    version='1.1',

    description='A Network Unit Test System',
    long_description=long_description,

    url='https://github.com/HSRNetwork/Nuts',

    author='Andreas Stalder, David Meister, Matthias Gabriel',
    author_email='astalder@hsr.ch, dmeister@hsr.ch, mgabriel@hsr.ch',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Networking',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
    ],

    keywords='network testing unit system',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['pyyaml', 'salt', 'pykwalify', 'colorama', 'salt-pepper'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={'pytest'},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'


    data_files=[('lib/python2.7/site-packages/nuts/service', ['nuts/service/testSchema.yaml'])],


    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'nuts = nuts.nuts:main',
        ],
    },
)
