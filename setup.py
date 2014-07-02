#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""

"""
__author__ = 'Martin Martimeo <martin@martimeo.de>'
__date__ = '02.07.14 - 16:53'

from distutils.core import setup

setup(
    name='bb2md',
    version='0.0.1',
    author='Martin Martimeo',
    author_email='martin@martimeo.de',
    url='https://github.com/MartinMartimeo/bb2md',
    packages=['bb2md'],
    license='GNU AGPLv3+ or BSD-3-clause',
    platforms='any',
    description='convert bbcode to markdown',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').readlines(),
    download_url='http://pypi.python.org/pypi/bb2md',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
