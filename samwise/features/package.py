# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os
import shutil

import docker
from nested_lookup import nested_lookup
from pip._internal.locations import USER_CACHE_DIR


def check_docker(image_name):
    client = docker.from_env()
    if not client.images.list(name=image_name):
        print(f'  - Pre-fetching {image_name}')
        client.images.pull(image_name)

    return client


def get_python_runtime_image(parsed_template_obj):
    runtimes = nested_lookup('Runtime', parsed_template_obj)

    if len(runtimes) > 1:
        raise Exception('Multiple python runtimes are not supported')

    runtime = runtimes[0]
    if 'python' not in runtime.lower():
        raise Exception(f'Only Python runtimes are supported, found {runtime}')

    lambda_python_containers = {"python3.8": "lambci/lambda:build-python3.8",
                                "python3.7": "lambci/lambda:build-python3.7",
                                "python3.6": "lambci/lambda:build-python3.6"}

    return runtime, lambda_python_containers[runtime]


def build(parsed_template_obj, output_location, base_dir):
    runtime, docker_image = get_python_runtime_image(parsed_template_obj)
    print(f' - Found Python runtime {runtime}')
    client = check_docker(docker_image)

    code_path = parsed_template_obj['Globals']['Function']['CodeUri']
    command = f"/bin/sh -c \"pip install pip --upgrade && pip install " \
              f"--cache-dir=/tmp/pip -r /the_project/requirements.txt -t /app/ && " \
              f"cp -r /the_project/{code_path} /app && cp -r /the_project/data /app/data\""

    output_location = os.path.abspath(output_location)
    base_dir = os.path.abspath(base_dir)
    volumes = {f"{output_location}/pkg": {"bind": "/app", "mode": "rw"},
               f"{base_dir}": {"bind": "/the_project", "mode": "ro"},
               f"{USER_CACHE_DIR}": {"bind": "/tmp/pip", "mode": "rw"}}

    print(f" - Building Package using Docker {docker_image}")
    shutil.rmtree(f"{output_location}/pkg/")
    os.mkdir(f"{output_location}/pkg/")
    container = client.containers.run(image=docker_image,
                                      command=command,
                                      volumes=volumes,
                                      remove=True,
                                      detach=True)
    for line in container.logs(stream=True):
        print(f"   > {line.decode('utf-8')}", end='', flush=True)

    return True
