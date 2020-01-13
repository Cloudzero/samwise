# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os.path
import re
import secrets
import string
import textwrap
from pathlib import Path

from ruamel.yaml import YAML
from voluptuous import REMOVE_EXTRA, All, Length, Optional, Required, Schema

from samwise import constants
from samwise.constants import FILE_INCLUDE_REGEX
from samwise.exceptions import UnsupportedSAMWiseVersion, InlineIncludeNotFound
from samwise.utils.tools import finditer_with_line_numbers, yaml_dumps


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
    YAML().dump(template_yaml_obj, out)


def parse(template_obj, metadata):
    processed_variables = {}
    variables = metadata.get(constants.VARS_KEY, [])

    for var in variables:
        if not isinstance(var, dict):
            value = input(f" - {var} : ")
            processed_variables[var] = value
        else:
            processed_variables.update(var)

    yaml_string = yaml_dumps(template_obj)
    include_matches = finditer_with_line_numbers(FILE_INCLUDE_REGEX, yaml_string)

    # find and handle the special #{include <filename>} syntax in templates
    for match, line_number in include_matches:
        prefix, file_name = match.groups()
        # create a random token name (no collisions!) to replace the include token with
        random_string = ''.join(secrets.choice(string.ascii_lowercase) for i in range(12))
        file_path = os.path.abspath(file_name)
        if os.path.exists(file_path):
            # match 0 is the string before match 1, we use the len of that to ensure we align the YAML correctly
            inline_file = textwrap.indent(Path(file_path).read_text(), ' ' * len(prefix))

            # add the inline file contents to processed variables for later render
            processed_variables[f"{random_string}"] = f"!Sub |\n{inline_file}"

            # mutate yaml_string with new random token
            yaml_string = re.sub(r"#{{include {file_name}}}".format(file_name=file_name),
                                 f"#{{{random_string}}}",
                                 yaml_string)
        else:
            # if we can't find the file, drop out here
            raise InlineIncludeNotFound(f"Line {line_number}: Could not find inline include file {file_path}")

    # Render the now ready template and variables
    rendered_template = __render_samwise_template(yaml_string, processed_variables)
    rendered_template_obj = YAML().load(rendered_template)

    # explicitly set the code uri for each function in preparation of packaging
    for k, v in rendered_template_obj['Resources'].items():
        if v.get('Type') == 'AWS::Serverless::Function':
            rendered_template_obj['Resources'][k]['Properties']['CodeUri'] = 'samwise-pkg.zip'

    return len(processed_variables), rendered_template_obj


def __render_samwise_template(template_string, replacement_map):
    prepared_template = SamTemplate(template_string)
    return prepared_template.safe_substitute(**replacement_map)


class SamTemplate(string.Template):
    delimiter = '#'
