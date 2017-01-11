Nuts - Network Unit Testing System
#############

Ein Network Unit Testing System das Netzwerke automatisch Testes. Bis jetzt werden Arista, Cisco und Linux Geräte unterstützt.


Installation
============

The following Python versions are fully supported:

- Python 2.7


Install on arch linux
----------------
TODO

Install on ubuntu
----------------
TODO

Install with pip
----------------

The recommended way to install nuts is using `pip <http://pip.readthedocs.org/en/latest/>`_:

::

    $ sudo pip install -U nuts

This will automatically install the latest version from the `Python Package
Index <https://pypi.python.org/pypi/nuts/>`__.

Manual Installation
-------------------

Get code::

    $ wget https://github.com/asta1992/nuts/archive/v0.3.0.zip
    $ unzip v0.3.0.zip
    $ cd nuts-1.0.0

Install::

    $ sudo python setup.py install

Usage
=======

usage: nuts.py [-h] [-i INPUT INPUT] [-v VALIDATE VALIDATE] [-vt VALIDATETEST]
               [-vd VALIDATEDEVICE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT INPUT, --input INPUT INPUT
                        Start with a Testfile and a Devicefile
  -v VALIDATE VALIDATE, --validate VALIDATE VALIDATE
                        Creates local account
  -vt VALIDATETEST, --validatetest VALIDATETEST
                        Creates local account
  -vd VALIDATEDEVICE, --validatedevice VALIDATEDEVICE
                        Creates local account


License
=======

The MIT License (MIT)

Copyright (c) 2016 Andreas Stalder, David Meister

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
