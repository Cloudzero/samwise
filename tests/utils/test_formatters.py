# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import pytest

from samwise.utils.formatters import to_camel_case


def test_to_camel_case():
    expected_output = "thisIsATest"
    output = to_camel_case("this-is-a-test")
    assert expected_output == output

    output = to_camel_case("this_is_a_test")
    assert expected_output == output

    with pytest.raises(ValueError):
        to_camel_case("This is a test")
