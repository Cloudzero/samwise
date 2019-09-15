# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os.path
import sys
from pathlib import Path

from ruamel.yaml import YAML
from voluptuous import Schema, Any, All, Length, Required, Optional, MultipleInvalid, Invalid, ALLOW_EXTRA

from samwise import constants
from samwise.exceptions import UnsupportedSAMWiseVersion


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
    })

    metadata = samwise_obj.get(constants.SAMWISE_METADATA_KEY)
    try:
        samwise_metadata = samwise_schema(metadata)

        if samwise_metadata.get('SamTemplate'):
            template_obj = yaml.load(samwise_metadata.get('SamTemplate'))
        else:
            template_obj = samwise_obj
            # remove SAMWise Metadata from template
            del template_obj[constants.SAMWISE_METADATA_KEY]

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
