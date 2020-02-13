# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os.path
import re
import textwrap
from pathlib import Path

from ruamel.yaml import YAML
from voluptuous import REMOVE_EXTRA, All, Length, Optional, Required, Schema

from samwise.constants import VARS_KEY, FILE_INCLUDE_REGEX, CFN_METADATA_KEY, SAMWISE_KEY, STACK_NAME_KEY, \
    NAMESPACE_KEY, ACCOUNT_ID_KEY, TAGS_KEY
from samwise.exceptions import UnsupportedSAMWiseVersion, InlineIncludeNotFound
from samwise.utils.tools import finditer_with_line_numbers


def load(input_file_name, namespace, aws_account_id=None):
    full_path_name = os.path.abspath(input_file_name)
    template_text = Path(full_path_name).read_text()

    system_vars = {f"{SAMWISE_KEY}::{ACCOUNT_ID_KEY}": aws_account_id or "**AWS ACCOUNT ID TBD**",
                   f"{SAMWISE_KEY}::{NAMESPACE_KEY}": namespace}
    template_text = search_and_replace_samwise_variables(template_text, system_vars)
    samwise_obj = YAML().load(template_text)

    samwise_schema = Schema({
        Required('Version'): "1.0",
        Required('DeployBucket'): All(str, Length(min=3, max=63)),
        Required(STACK_NAME_KEY): str,
        Optional(TAGS_KEY): list,
        Optional(VARS_KEY): list,
        Optional('Template'): str
    }, extra=REMOVE_EXTRA)

    try:
        samwise_metadata = samwise_schema(samwise_obj[CFN_METADATA_KEY][SAMWISE_KEY])
        if samwise_metadata.get('Template'):
            template_path_name = os.path.join(os.path.dirname(full_path_name), samwise_metadata.get('Template'))
            template_text = Path(template_path_name).read_text()

        # Add stack name and system vars
        system_vars_list = [{k: v} for k, v in system_vars.items()]
        if not samwise_metadata.get(VARS_KEY):
            samwise_metadata[VARS_KEY] = system_vars_list
        else:
            samwise_metadata[VARS_KEY] += system_vars_list
        samwise_metadata[VARS_KEY] += [{f"{SAMWISE_KEY}::{STACK_NAME_KEY}": samwise_metadata[STACK_NAME_KEY]}]

        # Add tags
        if not samwise_metadata.get(TAGS_KEY):
            samwise_metadata[TAGS_KEY] = [{"StackName": samwise_metadata[STACK_NAME_KEY]}]
        else:
            samwise_metadata[TAGS_KEY] += [{"StackName": samwise_metadata[STACK_NAME_KEY]}]

    except Exception as error:
        raise UnsupportedSAMWiseVersion(f"Unsupported or invalid SAMWise Template '{error}'")

    template_obj = parse(template_text, samwise_metadata)
    return template_obj, samwise_metadata


def save(template_yaml_obj, output_file_location):
    output_file = f"{output_file_location}/template.yaml"
    os.makedirs(output_file_location, exist_ok=True)
    out = Path(output_file)
    YAML().dump(template_yaml_obj, out)


def parse(template_text, metadata):
    processed_variables = {}
    variables = metadata.get(VARS_KEY, [])

    for var in variables:
        if not isinstance(var, dict):
            value = input(f" - {var} : ")
            processed_variables[var] = value
        else:
            processed_variables.update(var)

    template_text = search_and_replace_file_include_token(template_text)
    template_text = search_and_replace_samwise_variables(template_text, processed_variables)
    final_template_obj = YAML().load(template_text)

    # explicitly set the code uri for each function in preparation of packaging
    for k, v in final_template_obj['Resources'].items():
        if v.get('Type') == 'AWS::Serverless::Function':
            final_template_obj['Resources'][k]['Properties']['CodeUri'] = 'samwise-pkg.zip'

    return final_template_obj


def search_and_replace_samwise_variables(yaml_string, variables):
    for var_name, var_value in variables.items():
        match_string = "#{{{var_name}}}".format(var_name=var_name)
        yaml_string = re.sub(match_string,
                             var_value,
                             yaml_string)
    return yaml_string


def search_and_replace_file_include_token(yaml_string):
    include_matches = finditer_with_line_numbers(FILE_INCLUDE_REGEX, yaml_string)
    # find and handle the special #{SAMWise::include <filename>} syntax in templates
    for match, line_number in include_matches:
        prefix, file_name = match.groups()
        file_path = os.path.abspath(file_name)
        if os.path.exists(file_path):
            # We use the len of prefix to align the YAML correctly
            inline_file = textwrap.indent(Path(file_path).read_text(), ' ' * len(prefix))

            match_string = "['\"]#{{{samwise_key}::include {file_name}}}['\"]".format(samwise_key=SAMWISE_KEY,
                                                                                      file_name=file_name)
            yaml_string = re.sub(match_string,
                                 f"!Sub |\n{inline_file}",
                                 yaml_string)
        else:
            # if we can't find the file, drop out here
            raise InlineIncludeNotFound(f"Error on line {line_number}: Could not find inline include file {file_path}")
    return yaml_string
