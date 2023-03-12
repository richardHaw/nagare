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


class NodeDummy(object):
    """
    Creates a dummy object for app_py.main to run with.

    **parameters**, **types**, **return** and **return types**

    :param obj_data: A dict containing a node's basic data.
    :type obj_data: object
    """

    def __str__(self):
        return __name__

    def __init__(self, obj_data):
        self.obj_data = obj_data

        self.name = obj_data["name"]
        self.class_name = obj_data["class"]
        self.description = obj_data["description"]
        self.command = obj_data["command"]
        self.x = obj_data["x"]
        self.y = obj_data["y"]
        self.uuid = obj_data["uuid"]
        self.out_nodes = obj_data["out_nodes"]
        self.in_node = obj_data["in_node"]
        self.error = False
        self.skip = False
        self.dirty = False
        self.state_label = None

        self._errors_list = list()
        self.messages = list()

    def setErrors(self, errors):
        self._errors_list = errors

    def getErrors(self):
        return self._errors_list
