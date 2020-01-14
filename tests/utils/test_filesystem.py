# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os
import hashlib
import pytest

from samwise.utils.filesystem import hash_directory


@pytest.fixture(scope="module")
def test_folder(request):
    return "tests/data/"


def test_hash_directory(test_folder):
    result = hash_directory(test_folder)
    assert result == "21d1bc363d555ade661d693368e601e03b73370923a63c2c7a7af7eaaa3157d8"