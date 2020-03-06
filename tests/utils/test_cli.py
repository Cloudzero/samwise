# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from samwise.utils.cli import execute_and_process


def test_execute_and_process(capsys):
    result = execute_and_process(['echo', 'hello'])
    captured = capsys.readouterr()
    assert captured.out == "hello\r\n"
    assert result == 0

    result = execute_and_process(['printenv', 'ENVVAR'], env={'ENVVAR': 'VALUE'})
    captured = capsys.readouterr()
    assert captured.out == "VALUE\r\n"
    assert result == 0

    execute_and_process(['echo', 'hello'], status_only=True)
    captured = capsys.readouterr()
    assert captured.out == ".done\n"
