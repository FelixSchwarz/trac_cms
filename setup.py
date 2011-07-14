#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import setuptools


if __name__ == '__main__':
    version='0.1'
    setuptools.setup(
        name='TracCMS',
        version=version,
        
        description='Simple CMS based on Trac',
        author='Felix Schwarz',
        author_email='felix.schwarz@oss.schwarz.eu',
        license='MIT',
        install_requires=['Trac >= 0.11'],
        tests_require=['TracDevPlatformPlugin'],
        
        zip_safe=False,
        packages=setuptools.find_packages(exclude=['tests']),
        include_package_data=True,
        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Framework :: Trac',
        ],
        entry_points = {
            'trac.plugins': [
                'trac_cms = trac_cms',
            ]
        }
    ),


