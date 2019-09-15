# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


class TemplateNotFound(Exception):
    """Thrown if we could not find a valid SAMWise template"""
    pass


class UnsupportedSAMWiseVersion(Exception):
    """The SAMWise version that was read is unsupported"""
    pass
