#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from pip.req import parse_requirements
from setuptools import setup, find_packages

requirements = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in requirements]
readme = open('README.rst').read()

setup(name='nuts',
      version='1.1',
      description='A Network Unit Test System',
      author='Andreas Stalder, David Meister, Matthias Gabriel, Urs Baumann',
      author_email='astalder@hsr.ch, dmeister@hsr.ch, mgabriel@hsr.ch, ubaumann@ins.hsr.ch',
      url='https://github.com/HSRNetwork/Nuts',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      license='MIT',
      keywords='network testing unit system',
      long_description=readme,
      install_requires=reqs,
      entry_points={
          'console_scripts': [
              'nuts = nuts.main:main',
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',

          'Intended Audience :: Developers',
          'Topic :: System :: Networking',

          'License :: OSI Approved :: MIT License',

          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
      ],
      )
