# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2021 richardHaw

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function

import os
import logging
from datetime import datetime
from app_py.configs import config_obj
LOG_OBJ = None


def getLogger(log_path=None):
    """
    Use this to find a handler with specified name.
    Also sets the formatter.

    **parameters**, **types**, **return** and **return types**

    :param log_path: Output folder.
    :type log_path: str

    :return: Log handler object.
    :rtype: pointer

    - Example::

        logUtils.getLogger("nagare_logger")
    """

    global LOG_OBJ

    if LOG_OBJ:
        return LOG_OBJ

    handler = setupHandler(log_path)

    LOG_OBJ = logging.getLogger()
    LOG_OBJ.setLevel(logging.DEBUG)
    LOG_OBJ.addHandler(handler)
    LOG_OBJ.propagate = True

    if [h for h in LOG_OBJ.handlers if isinstance(h, logging.StreamHandler)]:
        LOG_OBJ.addHandler(logging.StreamHandler())

    LOG_OBJ.info("Log initiated...")
    return LOG_OBJ


def timeStamp():
    """
    Used to get a date/time stamp.
    The format is yearMonthDay_{hour_minute_secs) or 20201024_{18_22_15}

    **parameters**, **types**, **return** and **return types**

    :return: A time and date stamp as string.
    :rtype: str

    - Example::

        logUtils.Logs.timeStamp()
    """

    time = datetime.now
    year = str(time().year).zfill(2)
    month = str(time().month).zfill(2)
    day = str(time().day).zfill(2)
    hour = str(time().hour).zfill(2)
    minute = str(time().minute).zfill(2)
    secs = str(time().second).zfill(2)
    out = "{}{}{}_{{{}_{}_{}}}".format(year, month, day, hour, minute, secs)
    return out


def setupHandler(log_path=None):
    kill()

    if log_path:
        log_full_path = os.path.join(config_obj.get("PATHS", "log_path"), log_path)
        if not os.path.isdir(os.path.dirname(log_full_path)):
            os.makedirs(os.path.dirname(log_full_path))
        handler = logging.FileHandler(log_full_path)
        print("Log file: {}".format(log_full_path))
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter("%(levelname)s %(asctime)s (%(module)s): %(message)s",
                                           "%H:%M:%S"))
    if LOG_OBJ:
        LOG_OBJ.addHandler(handler)
        LOG_OBJ.propagate = True

    return handler


def setLogLevel():
    LOG_OBJ.setLevel(logging.INFO)


def getDatedName(filename):
    """
    Returns a name with a date stamp.

    **parameters**, **types**, **return** and **return types**

    :param filename: The string you want to be appended.
    :type filename: str

    :return: A time and date stamp as string.
    :rtype: str

    - Example::

        logUtils.Logs.getDatedName("MyLogName")
    """

    return "{}_{}_".format(filename, timeStamp())


def kill():
    if LOG_OBJ:
        for handler in LOG_OBJ.handlers:
            LOG_OBJ.removeHandler(handler)
            print("Log killed:", handler)
