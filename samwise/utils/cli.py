# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import errno
import os
import pty
import sys
from select import select
from subprocess import Popen


def execute_and_process(command, env=None):
    """Largely found in https://stackoverflow.com/a/31953436"""
    masters, slaves = zip(pty.openpty(), pty.openpty())

    if env:
        my_env = {**os.environ.copy(), **env}
    else:
        my_env = {**os.environ.copy()}
    with Popen(command, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1], env=my_env) as p:
        for fd in slaves:
            os.close(fd)  # no input
            readable = {
                masters[0]: sys.stdout.buffer,  # store buffers separately
                masters[1]: sys.stderr.buffer,
            }
        while readable:
            for fd in select(readable, [], [])[0]:
                try:
                    data = os.read(fd, 15)  # read available
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise  # XXX cleanup
                    del readable[fd]  # EIO means EOF on some systems
                else:
                    if not data:  # EOF
                        del readable[fd]
                    else:
                        if fd == masters[0]:  # We caught stdout
                            print(data.decode('utf-8'), end='', flush=True)
                        else:  # We caught stderr
                            print(data.decode('utf-8'), end='', flush=True)
                        readable[fd].flush()
    for fd in masters:
        os.close(fd)
    return p.returncode
