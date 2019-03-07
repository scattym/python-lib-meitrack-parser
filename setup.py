from setuptools import setup, find_packages

setup(
    name='meitrackparser',
    version='2.7.dev0',
    description='A library for parsing meitrack gprs data',
    url='https://bitbucket.org/poslive/python-lib-meitrack-parser.git',
    author='Matt Clark',
    author_email='mattjclark0407@hotmail.com',
    license='Copyright (C) Matt Clark - All Rights Reserved',
    packages=find_packages(),
    install_requires=[
        'licenseparser',
    ],
    dependency_links=[
    ],
    zip_safe=True
)
