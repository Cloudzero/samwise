# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


class TemplateNotFound(Exception):
    """Thrown if we could not find a template, either SAMWise or SAM, to load"""
    pass


class UnsupportedSAMWiseVersion(Exception):
    """The SAMWise version that was read is unsupported"""
    pass


class InlineIncludeNotFound(Exception):
    """Thrown if we could not find the inline include file"""
    pass


class InvalidSAMWiseTemplate(Exception):
    """Thrown if we the template we loaded was not a valid SAMWise template"""
    pass
