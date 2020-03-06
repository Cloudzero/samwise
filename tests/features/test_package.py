# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from samwise.features.package import get_python_runtime_image
import samwise.features.template as handler


def test_get_python_runtime_image(valid_template, namespace):
    template_path, obj, metadata = handler.load(valid_template, namespace)
    runtime, image = get_python_runtime_image(obj)

    assert runtime == "python3.7"
    assert image == "lambci/lambda:build-python3.7"
