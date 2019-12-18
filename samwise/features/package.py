# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import docker
from nested_lookup import nested_lookup


def check_docker(runtimes):
    client = docker.from_env()
    print(client.images.list())
    lambda_python_containers = {"python3.7": "lambci/lambda:python3.7",
                                "python3.6": "lambci/lambda:python3.6"}

    for runtime in runtimes:
        print(f'fetching {runtime}')
        client.images.pull(lambda_python_containers[runtime])

    print(client.images.list())
    return client


def get_python_runtimes(parsed_template_obj):
    # check if runtime is global or by function
    python_runtimes = nested_lookup('Runtime', parsed_template_obj)
    print(python_runtimes)

    return python_runtimes


def create(parsed_template_obj, output_location, base_dir, aws_creds, s3_bucket):
    python_runtimes = get_python_runtimes(parsed_template_obj)

    result = check_docker(python_runtimes)

    """
    docker run --rm -it -v $(pwd)/.samwise/build:/app -v $(pwd):/src lambci/lambda:build-python3.7 /bin/sh -c "pip install pip --upgrade && pip install -r /src/requirements.txt -t /app/ && cp -r /src/cz /app/cz && cp -r /src/data /app/data"
    """

    return result
