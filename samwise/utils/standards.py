# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN

import dateutil.parser as parser
from dateutil.tz import tzutc


def isodatetimenow():
    return datetime.now(tz=timezone.utc).isoformat()


def isodatetime(datetime_string):
    return parser.parse(datetime_string).isoformat()


def parse_to_datetime(datetime_string):
    return parser.parse(datetime_string)


def utctimestamp():
    return Decimal(str(datetime.now(tz=timezone.utc).timestamp())).quantize(Decimal(".00000"), rounding=ROUND_DOWN)


def utc_iso_from_anything(input_data):
    """
    >>> utc_iso_from_anything(None)


    >>> utc_iso_from_anything(1571265346.021007)
    '2019-10-16T22:35:46.021007+00:00'

    >>> utc_iso_from_anything(1572274216685)
    '2019-10-28T14:50:16.685000+00:00'

    >>> utc_iso_from_anything('2019-10-16T22:35:46.021007+00:00')
    '2019-10-16T22:35:46.021007+00:00'

    >>> utc_iso_from_anything('2019-10-16T22:35:46.021007-04:00')
    '2019-10-17T02:35:46.021007+00:00'

    >>> utc_iso_from_anything('2019-10-16T22:35')
    '2019-10-17T02:35:00+00:00'

    >>> utc_iso_from_anything('January 1, 2047 at 8:21:00AM')
    '2047-01-01T13:21:00+00:00'

    """
    if input_data is None:
        return None

    if isinstance(input_data, str):
        return parser.parse(input_data).astimezone(tzutc()).isoformat()
    else:
        # if it's larger than the max size for a 32 bit integer it's in ms
        if input_data > 2147483647:
            input_data = input_data / 1000
        return datetime.fromtimestamp(input_data, tz=timezone.utc).isoformat()
