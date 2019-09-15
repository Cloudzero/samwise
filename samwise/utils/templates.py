# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import string


class SamTemplate(string.Template):
    delimiter = '#'


def render_template(template_string, replacement_map):
    prepared_template = SamTemplate(template_string)
    return prepared_template.safe_substitute(**replacement_map)
