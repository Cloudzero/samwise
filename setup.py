# Copyright (c) CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from samwise import __version__
from setuptools import setup, find_packages


PROJECT_URL = "https://github.com/Cloudzero/samwise"

setup(
    name='samwise',
    version=__version__,
    description='SAMWise is a tool for packaging and deploying AWS Serverless Application Model applications',
    long_description="Please visit {}.".format(PROJECT_URL),
    author='CloudZero',
    author_email='support@cloudzero.com',
    url=PROJECT_URL,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['samwise=samwise.__main__:main']
    },
    package_data={'samwise': ['data/*']},
    include_package_data=True,
    install_requires=[
        'boto3>=1.10.41',
        'docopt>=0.6.2',
        'aws-sam-cli>=0.38.0',
        'awscli>=1.16.305',
        'ruamel.yaml>=0.16.5',
        'voluptuous>=0.11.7',
        'docker',
        'nested-lookup',
        'pip>=19.3.1'
    ],
    license="MIT",
    zip_safe=False,
    keywords='SAM AWS CloudZero Serverless',
    platforms=['MacOS', 'Unix'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Unix'
    ],
)
