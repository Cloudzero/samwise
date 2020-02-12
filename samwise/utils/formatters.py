# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


def to_camel_case(input_string):
    """
    Based on https://stackoverflow.com/a/19053800

    Args:
        input_string (str):

    Returns:
        (str):
    """
    if "-" in input_string:
        components = input_string.split('-')
    elif "_" in input_string:
        components = input_string.split('_')
    else:
        raise ValueError("Only kebab or snake case strings supported")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + ''.join(x.title() for x in components[1:])
