# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal

import dateutil.parser as parser


def isodatetimenow():
    return datetime.now(tz=timezone.utc).isoformat()


def isodatetime(datetime_string):
    return parser.parse(datetime_string).isoformat()


def parse_to_datetime(datetime_string):
    return parser.parse(datetime_string)


def utctimestamp():
    return Decimal(str(datetime.now(tz=timezone.utc).timestamp())).quantize(Decimal(".00000"), rounding=ROUND_DOWN)
