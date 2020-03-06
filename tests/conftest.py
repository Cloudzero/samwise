# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from pathlib import Path

import pytest

valid_templates = ['tests/data/samwise.yaml', 'tests/data/linked-samwise.yaml']


@pytest.fixture(params=valid_templates, scope="module")
def valid_template(request):
    return request.param


@pytest.fixture(scope="module")
def missing_template():
    return 'tests/data/non-existent-template-file.yaml'


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
def include_template():
    return 'tests/data/include-samwise.yaml'


@pytest.fixture(scope="module")
def accountid_template():
    return 'tests/data/accountid-samwise.yaml'


@pytest.fixture(scope="module")
def include_data():
    return Path('tests/data/MyStateMachine.json').read_text()


@pytest.fixture(scope="module")
def namespace():
    return 'little-bunny-foo-foo'