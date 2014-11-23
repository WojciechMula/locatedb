# -*- coding: utf-8 -*-
from distutils.core import setup

def get_readme():
    with open('README') as f:
        return f.read()


setup(
    name                = 'locatedb',
    version             = '1.0.0',
    description         = "",
    author              = "Wojciech Muła",
    author_email        = "wojciech_mula@poczta.onet.pl",
    maintainer          = "Wojciech Muła",
    maintainer_email    = "wojciech_mula@poczta.onet.pl",
    url                 = "http://github.com/WojciechMula/locatedb",
    license             = "BSD (3 clauses)",
    long_description    = get_readme(),
    packages            = ['locatedb'],
    package_dir         = {'locatedb': ''},
    scripts             = ["locatedb.py"],
    keywords            = [
        "locate",
        "compression",
    ],
    classifiers         = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System",
    ],
)

