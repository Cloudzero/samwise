# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import errno
import os
import pty
import sys
from select import select
from subprocess import Popen


def execute_and_process(command, env=None, status_only=False):
    """
    Run a shell command in a subprocess while streaming the results
    Based on https://stackoverflow.com/a/31953436

    The extreme complexity of this function is due to the desire to
        1. Stream the results in real time (not so hard)
        2. Support terminal colors (apparently hard)
        3. Use existing term width (also apparently hard)

    Those three requirements necessitated what you see here, if you find a simpler alternative
    please let me know, because I think this is ridiculous

    Args:
        command (list): Command to run
        env (dict): Environment vars to inject into the shell
        status_only (bool): Dont display the output, but do indicate something is happening

    Returns:

    """
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
                    data = os.read(fd, 5)  # read available, 5 bytes at a time
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise  # XXX cleanup
                    del readable[fd]  # EIO means EOF on some systems
                else:
                    if not data:  # EOF
                        del readable[fd]
                    else:
                        if status_only:
                            print('.', end='', flush=True)
                        else:
                            if fd == masters[0]:  # We caught stdout
                                print(data.decode('utf-8'), end='', flush=True)
                            else:  # We caught stderr
                                print(data.decode('utf-8'), end='', flush=True)
                        readable[fd].flush()
    for fd in masters:
        os.close(fd)
    if status_only:
        print('done')
    return p.returncode
