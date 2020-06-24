# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import os
import re
import shutil
import sys
from pathlib import Path

import docker
from colorama import Fore
from nested_lookup import nested_lookup
from pip._internal.locations import USER_CACHE_DIR
from samwise.utils.filesystem import get_lambda_package_size


def check_docker(image_name):
    client = docker.from_env()
    if not client.images.list(name=image_name):
        print(f'     - Pre-fetching {image_name}')
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


def build(parsed_template_obj, output_location, base_dir, cache_dir):
    runtime, docker_image = get_python_runtime_image(parsed_template_obj)
    print(f'   - Found Python runtime {runtime}')
    client = check_docker("lambci/lambda:latest")

    code_path = parsed_template_obj['Globals']['Function']['CodeUri']
    command = f"/bin/sh -c \"yum install -y snappy-devel && " \
              f"pip install pip --upgrade && " \
              f"pip uninstall awscli aws-sam-cli -y && " \
              f"chown -R $UID /tmp/pip && " \
              f"pip install --cache-dir=/tmp/pip -r /the_project/requirements.txt -t /app/ && " \
              f"cp -rf /usr/lib64/libsnappy.* /app/ && " \
              f"cp -r /the_project/{code_path} /app && cp -r /the_project/data /app/data && " \
              f"chown -R {os.getuid()} /app /tmp/pip\""

    output_location = os.path.abspath(output_location)
    base_dir = os.path.abspath(base_dir)
    cache_dir = os.path.abspath(cache_dir or USER_CACHE_DIR)
    volumes = {f"{output_location}/pkg": {"bind": "/app", "mode": "rw"},
               f"{base_dir}": {"bind": "/the_project", "mode": "ro"},
               f"{cache_dir}": {"bind": "/tmp/pip", "mode": "rw"}}

    print(f"   - Building Package using Docker {docker_image}")
    shutil.rmtree(f"{output_location}/pkg/", ignore_errors=True)
    os.mkdir(f"{output_location}/pkg/")
    container = client.containers.run(image=docker_image,
                                      command=command,
                                      volumes=volumes,
                                      remove=True,
                                      detach=True)
    for line in container.logs(stream=True):
        print(f"     > {line.decode('utf-8')}", end='', flush=True)

    return True


def slim_package_folder(output_location):
    print(f"{Fore.LIGHTCYAN_EX} - Slimming package", end="")
    before_pkg_size = get_lambda_package_size(f"{output_location}/pkg/")
    pattern = re.compile(r"(dist-info|__pycache__|\.pyc|\.pyo$)")
    package_files = Path(f"{output_location}/pkg").glob('**/*')
    for file in package_files:
        if pattern.search(file.name):
            if file.is_dir():
                # print(f"Delete folder: {file.name}")
                shutil.rmtree(str(file))
            else:
                # print(f"Delete file  : {file.name}")
                file.unlink(missing_ok=True)
            print('.', end="")
    print(f"{Fore.RESET}")

    final_pkg_size = get_lambda_package_size(f"{output_location}/pkg/")
    if final_pkg_size > 250:
        print(f"\n{Fore.LIGHTRED_EX}ERROR{Fore.RESET}: Package would be over 250 MB limit ({final_pkg_size:.1f} MB)\n"
              f"       Refactor your package requirements and try again.")
        sys.exit(1)
    else:
        print(f"   - Reduced package size from {before_pkg_size:.1f} MB to {final_pkg_size:.1f} MB")
