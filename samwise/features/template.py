# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os.path
import re
import textwrap
from pathlib import Path

from ruamel.yaml import YAML
from voluptuous import REMOVE_EXTRA, All, Length, Optional, Required, Schema, Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error

from samwise.constants import VARS_KEY, FILE_INCLUDE_REGEX, CFN_METADATA_KEY, SAMWISE_KEY, STACK_NAME_KEY, \
    NAMESPACE_KEY, ACCOUNT_ID_KEY, TAGS_KEY, SAMWISE_TEMPLATE_FILE_NAME, AWS_SAM_TEMPLATE_FILE_NAME, \
    SAMWISE_SUPPORTED_VERSIONS, DEPLOY_BUCKET_KEY
from samwise.exceptions import UnsupportedSAMWiseVersion, InlineIncludeNotFound, TemplateNotFound, \
    InvalidSAMWiseTemplate
from samwise.utils.tools import finditer_with_line_numbers


def load(file_name, namespace, aws_account_id=None):
    template_text = None
    template_path = None
    input_file_names = list(filter(None, [file_name, SAMWISE_TEMPLATE_FILE_NAME, AWS_SAM_TEMPLATE_FILE_NAME]))

    while not template_text:
        for template_file in input_file_names:
            template_path = os.path.abspath(template_file)
            try:
                template_text = Path(template_path).read_text()
                break
            except FileNotFoundError:
                pass
        else:
            raise TemplateNotFound(f"No SAM or SAMWise template file could be found, "
                                   f"tried {', '.join(input_file_names)}")

    # By doing this here, we can support SAMWise vars even in the SAMWise metadata block
    aws_account_id = aws_account_id or f"{{{SAMWISE_KEY}::{ACCOUNT_ID_KEY}}}"
    namespace = namespace or f"{{{SAMWISE_KEY}::{NAMESPACE_KEY}}}"
    system_vars = {f"{SAMWISE_KEY}::{ACCOUNT_ID_KEY}": str(aws_account_id),
                   f"{SAMWISE_KEY}::{NAMESPACE_KEY}": namespace}
    template_text = search_and_replace_samwise_variables(template_text, system_vars)
    samwise_obj = YAML().load(template_text)

    samwise_schema = Schema({
        Required('Version'): str,
        Optional(DEPLOY_BUCKET_KEY): All(str, Length(min=5, max=63)),
        Required(STACK_NAME_KEY): str,
        Optional(TAGS_KEY): list,
        Optional(VARS_KEY): list,
        Optional('Template'): str
    }, extra=REMOVE_EXTRA)

    samwise_path = None
    try:
        samwise_metadata = samwise_schema(samwise_obj[CFN_METADATA_KEY][SAMWISE_KEY])
        if samwise_metadata.get('Template'):
            samwise_path = os.path.join(os.path.dirname(template_path), samwise_metadata.get('Template'))
            template_text = Path(samwise_path).read_text()
    except (Invalid, MultipleInvalid) as error:
        raise InvalidSAMWiseTemplate(f"SAMWise metadata is invalid "
                                     f"(error: {humanize_error(samwise_obj[CFN_METADATA_KEY][SAMWISE_KEY], error)})")
    except KeyError:
        raise InvalidSAMWiseTemplate(f"SAMWise metadata not found (template: {template_path})")
    except FileNotFoundError:
        raise TemplateNotFound(f"SAMWise template file could be found ({samwise_path})")
    except Exception as error:
        raise InvalidSAMWiseTemplate(f"Unexpected error processing SAMWise Template '{error}'")

    if samwise_metadata['Version'] not in SAMWISE_SUPPORTED_VERSIONS:
        raise UnsupportedSAMWiseVersion(f"SAMWise version {samwise_metadata['Version']} "
                                        f"is not supported by this version of SAMWise")

    # Add stack name to system vars (defined above) and combine with any user provided variables
    system_vars[f"{SAMWISE_KEY}::{STACK_NAME_KEY}"] = samwise_metadata[STACK_NAME_KEY]
    system_vars_list = [{k: v} for k, v in system_vars.items()]
    if not samwise_metadata.get(VARS_KEY):
        samwise_metadata[VARS_KEY] = system_vars_list
    else:
        samwise_metadata[VARS_KEY] += system_vars_list

    # Add tags
    if not samwise_metadata.get(TAGS_KEY):
        samwise_metadata[TAGS_KEY] = [{"StackName": samwise_metadata[STACK_NAME_KEY]}]
    else:
        samwise_metadata[TAGS_KEY] += [{"StackName": samwise_metadata[STACK_NAME_KEY]}]

    # add default deploy bucket (if needed)
    if not samwise_metadata.get(DEPLOY_BUCKET_KEY):
        samwise_metadata[DEPLOY_BUCKET_KEY] = f"samwise-deployment-{aws_account_id}"
    print(f"   - Deploy bucket is: {samwise_metadata[DEPLOY_BUCKET_KEY]}")

    template_obj = parse(template_text, samwise_metadata)
    return template_path, template_obj, samwise_metadata


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

    layers = final_template_obj['Globals']['Function'].get('Layers') or []
    if layers:
        print('  - Layers detected')
        for layer in layers:
            print(layer)

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
