# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
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
        'boto3>=1.12.15',
        'docopt>=0.6.2',
        'cfn-lint>=0.28.3'
        'awscli>=1.18.15',
        'pyyaml>=5.3',
        'ruamel.yaml>=0.16.10',
        'voluptuous>=0.11.7',
        'docker>=4.2.0',
        'nested-lookup>=0.2.21',
        'pip>=20.0.2',
        'colorama>=0.4.3',
        'aws-sam-cli>=0.53.0',
    ],
    license="MIT",
    zip_safe=False,
    keywords='SAM AWS CloudZero Serverless',
    platforms=['MacOS', 'Unix'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Unix'
    ],
)
