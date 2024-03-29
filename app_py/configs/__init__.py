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
import sys
from six.moves import configparser

config_file = os.getenv("NAGARE_CONFIGS", "")
if not os.path.exists(config_file):
    raise IOError("Invalid Path: NAGARE_CONFIGS")

config_obj = configparser.ConfigParser()
config_obj.read(config_file)
config_obj.set("PATHS", "mod_paths", eval(config_obj.get("PATHS", "mod_paths")))

for _module_path in config_obj.get("PATHS", "mod_paths"):
    if not os.path.exists(_module_path):
        continue
    if _module_path not in sys.path:
        sys.path.append(_module_path)

test_block = {"what": "This is Hawdini",
              "where": "Made in Japan",
              # "when": "On my spare time",
              "why": "To make a better world",
              "who": "Richard Haw"}
