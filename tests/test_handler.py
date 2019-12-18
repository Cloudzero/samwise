# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections import OrderedDict

import pytest

import samwise.features.template as handler

valid_templates = ['tests/data/samwise.yaml', 'tests/data/linked-samwise.yaml']


@pytest.fixture(params=valid_templates, scope="module")
def valid_template(request):
    return request.param


@pytest.fixture(scope="module")
def invalid_template():
    return 'tests/data/invalid-samwise.yaml'


@pytest.fixture(scope="module")
def non_samwise_template():
    return 'tests/data/non-samwise.yaml'


@pytest.fixture(scope="module")
def linked_template():
    return 'tests/data/linked-samwise.yaml'


@pytest.fixture(scope="module")
def namespace():
    return 'little-bunny-foo-foo'


def test_happy_path(valid_template, namespace):
    obj, metadata = handler.load(valid_template, namespace)
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


def test_non_samwise_template(non_samwise_template, namespace):
    with pytest.raises(Exception) as err:
        handler.load(non_samwise_template, namespace)
    assert 'invalid SAMWise Template' in str(err.value)


def test_invalid_samwise_template(invalid_template, namespace):
    with pytest.raises(Exception) as err:
        handler.load(invalid_template, namespace)
    assert 'invalid SAMWise Template' in str(err.value)
