# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import io
from collections import ChainMap

from ruamel.yaml import YAML

from samwise import constants
from samwise.utils.templates import render_template


def parse(template_obj, metadata):
    processed_variables = {}
    variables = metadata.get(constants.VARS_KEY, [])

    for var in variables:
        if not isinstance(var, dict):
            value = input(f" - {var} : ")
            processed_variables[var] = value
        else:
            processed_variables.update(dict(var))

    output = io.StringIO()
    yaml = YAML()
    yaml.dump(template_obj, output)

    parsed_template = render_template(output.getvalue(), processed_variables)
    parsed_template_obj = yaml.load(parsed_template)

    return parsed_template_obj
