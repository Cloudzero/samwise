# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import io
import os.path
import string
import sys
from pathlib import Path
from pprint import pprint

from ruamel.yaml import YAML

from samwise import constants
from samwise.exceptions import UnsupportedSAMWiseVersion
from voluptuous import REMOVE_EXTRA, All, Length, Optional, Required, Schema


def load(input_file_name, namespace):
    full_path_name = os.path.abspath(input_file_name)
    input_text = Path(full_path_name).read_text()
    yaml = YAML()
    samwise_obj = yaml.load(input_text)

    samwise_schema = Schema({
        Required('Version'): "1.0",
        Required('DeployBucket'): All(str, Length(min=3, max=63)),
        Required('StackName'): str,
        Optional('Variables'): list,
        Optional('SamTemplate'): str
    }, extra=REMOVE_EXTRA)

    try:
        metadata = samwise_obj[constants.CFN_METADATA_KEY][constants.SAMWISE_METADATA_KEY]
        samwise_metadata = samwise_schema(metadata)

        if samwise_metadata.get('SamTemplate'):
            template_obj = yaml.load(samwise_metadata.get('SamTemplate'))
        else:
            template_obj = samwise_obj

        # Add stack name and namespace to available variables
        try:
            samwise_metadata[constants.VARS_KEY].extend([{constants.STACK_NAME_KEY: metadata[constants.STACK_NAME_KEY]},
                                                        {constants.NAMESPACE_KEY: namespace}])
        except KeyError:
            samwise_metadata[constants.VARS_KEY] = [{constants.STACK_NAME_KEY: metadata[constants.STACK_NAME_KEY]},
                                                    {constants.NAMESPACE_KEY: namespace}]
    except Exception as error:
        raise UnsupportedSAMWiseVersion(f"Unsupported or invalid SAMWise Template '{error}'")

    return template_obj, samwise_metadata


def save(template_yaml_obj, output_file_location):
    output_file = f"{output_file_location}/template.yaml"
    os.makedirs(output_file_location, exist_ok=True)
    out = Path(output_file)
    yaml = YAML()
    yaml.dump(template_yaml_obj, out)


def display(template_obj):
    yaml = YAML()
    yaml.dump(template_obj, sys.stdout)


def parse(template_obj, metadata):
    processed_variables = {}
    variables = metadata.get(constants.VARS_KEY, [])

    for var in variables:
        if not isinstance(var, dict):
            value = input(f" - {var} : ")
            processed_variables[var] = value
        else:
            processed_variables.update(var)

    output = io.StringIO()
    yaml = YAML()
    yaml.dump(template_obj, output)

    parsed_template = render(output.getvalue(), processed_variables)
    parsed_template_obj = yaml.load(parsed_template)

    code_path = parsed_template_obj['Globals']['Function']['CodeUri']
    # print(code_path)
    for k, v in parsed_template_obj['Resources'].items():
        if v.get('Type') == 'AWS::Serverless::Function':
            parsed_template_obj['Resources'][k]['Properties']['CodeUri'] = 'pkg.zip'

    # pprint(parsed_template_obj)
    return parsed_template_obj


def render(template_string, replacement_map):
    prepared_template = SamTemplate(template_string)
    return prepared_template.safe_substitute(**replacement_map)


class SamTemplate(string.Template):
    delimiter = '#'
