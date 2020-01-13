# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import hashlib
import io
import re
import sys

from ruamel.yaml import YAML


def finditer_with_line_numbers(pattern, input_string, flags=0):
    """
    A version of 're.finditer' that returns '(match, line_number)' pairs.
    """

    matches = list(re.finditer(pattern, input_string, flags))
    if not matches:
        return []

    end = matches[-1].start()
    # -1 so a failed 'rfind' maps to the first line.
    newline_table = {-1: 0}
    for i, m in enumerate(re.finditer(r'\n', input_string), 1):
        # don't find newlines past our last match
        offset = m.start()
        if offset > end:
            break
        newline_table[offset] = i

    # Failing to find the newline is OK, -1 maps to 0.
    for m in matches:
        newline_offset = input_string.rfind('\n', 0, m.start())
        line_number = newline_table[newline_offset]
        yield m, line_number


def hash_string(input_string):
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


def yaml_dumps(input_yaml):
    """
    This function exists solely because the creator of Ruamel, an otherwise great YAML lib, refuses to support
    the most basic of use cases, the output of YAML as a string.

    He goes to great lengths to explain himself, but it makes no sense to me:
    - https://yaml.readthedocs.io/en/latest/example.html#output-of-dump-as-a-string
    - https://stackoverflow.com/a/47617341/771901

    I get that many developers might make poor choices and use strings as a bad solution to a problem they are solving
    but not supporting this use case is a pretty cynical and shortsighted position to take

    Args:
        input_yaml (object): YAML object

    Returns:
        str: YAML as string
    """
    output = io.StringIO()
    YAML().dump(input_yaml, output)
    return output.getvalue()


def yaml_print(template_obj):
    YAML().dump(template_obj, sys.stdout)
