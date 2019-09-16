# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections import OrderedDict
import pytest

import samwise.handler as handler


@pytest.fixture(scope="module")
def template_file_path():
    return 'tests/data/samwise.yaml'


@pytest.fixture(scope="module")
def namespace():
    return 'little-bunny-foo-foo'


def test_happy_path(template_file_path, namespace):
    obj, metadata = handler.load(template_file_path, namespace)
    assert obj
    assert metadata['Version'] == '1.0'
    assert metadata['DeployBucket'] == 'sample-deploy-bucket'
    assert metadata['StackName'] == 'MyStackName'
    assert metadata['Variables'] == [
        'PromptForVar',
        OrderedDict({'PreparedVar': 'PreparedValue'}),
        {'StackName': 'MyStackName'},
        {'Namespace': namespace}
    ]
