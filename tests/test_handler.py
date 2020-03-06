# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections import OrderedDict
from pathlib import Path

import pytest

import samwise.features.template as handler
from samwise.utils.tools import yaml_dumps


def test_happy_path(valid_template, namespace):
    template_path, obj, metadata = handler.load(valid_template, namespace)
    assert obj
    assert metadata['Version'] == '1.0'
    assert metadata['DeployBucket'] == 'sample-deploy-bucket'
    assert metadata['StackName'] == 'MyStackName'
    assert metadata['Variables'] == [
        OrderedDict({'PreparedVar': 'PreparedValue'}),
        {'SAMWise::AccountId': "{SAMWise::AccountId}"},
        {'SAMWise::Namespace': namespace},
        {'SAMWise::StackName': 'MyStackName'}
    ]
    assert obj['Parameters']['Namespace']['Default'] == namespace


def test_account_id(accountid_template, namespace):
    template_path, obj, metadata = handler.load(accountid_template, namespace, '123456789012')
    assert obj['Metadata']['SAMWise']['DeployBucket'] == 'sample-deploy-bucket-123456789012'


def test_include_samwise_template(include_template, include_data, namespace):
    template_path, obj, metadata = handler.load(include_template, namespace)
    assert obj
    yaml_string = yaml_dumps(obj['Resources']['MyStateMachine']['Properties']['DefinitionString'])
    assert yaml_string == f"!Sub |\n{include_data}\n"


def test_non_samwise_template(non_samwise_template, namespace):
    with pytest.raises(Exception) as err:
        handler.load(non_samwise_template, namespace)
    assert 'SAMWise metadata not found' in str(err.value)


def test_invalid_samwise_template(invalid_template, namespace):
    with pytest.raises(Exception) as err:
        handler.load(invalid_template, namespace)
    assert 'SAMWise metadata is invalid' in str(err.value)


def test_missing_samwise_template(missing_template, namespace):
    with pytest.raises(Exception) as err:
        handler.load(missing_template, namespace)
    assert 'No SAM or SAMWise template file could be found' in str(err.value)
