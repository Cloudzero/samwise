# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


import os
import sys
from subprocess import PIPE, Popen


def execute_and_process(command, transform=None, env=None):
    os.environ['PYTHONUNBUFFERED'] = "1"

    if env:
        my_env = {**os.environ.copy(), **env}
        proc = Popen(command, stdout=PIPE, stderr=PIPE, env=my_env)
    else:
        proc = Popen(command, stdout=PIPE, stderr=PIPE)

    if not transform:
        sys.stdout.write("   > ")

    for line in proc.stderr:
        if callable(transform):
            transform(f"    > {line.decode('utf-8')}", end='')
        else:
            sys.stdout.write('.')

    for line in proc.stdout:
        if callable(transform):
            transform(f"    > {line.decode('utf-8')}", end='')
        else:
            sys.stdout.write('.')

    if not transform:
        print('.')
