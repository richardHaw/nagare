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


class Spawn(object):
    def __str__(self):
        return __name__


    def __init__(self,status="error"):
        self._errors = list()
        self._messages = list()
        self._status = ""

        self.setStatus(status)


    def setStatus(self,stat):
        if stat not in ["error","skip"]:
            raise ValueError("Invalid status: {}".format(stat))
        self._status = stat


    def getStatus(self):
        return self._status


    def addError(self,new_err):
        try:
            self._errors.append(self._getErrorTuple(new_err))
        except KeyError as e:
            print(e,new_err)


    def appendErrors(self,new_errors):
        for e in new_errors:
            self.addError(e)


    def getErrors(self):
        all_errs = list()
        for e in self._errors:
            all_errs.append(self._getErrorDict(e))
        return all_errs


    def addMessage(self,msg_str):
        self._messages.append(" - {}".format(str(msg_str)))


    def appendMessages(self,new_messages):
        for m in new_messages:
            addMessage(m)


    def getMessages(self):
        return self._messages


    def _getErrorTuple(self,error_dict):
        _a = error_dict.get("item",None)
        _b = error_dict.get("type","")
        _c = error_dict.get("reason","")

        if _a is None:
            raise KeyError("Item not specified in error")

        return (str(_a),str(_b),str(_c))


    def _getErrorDict(self,err_tup):
        if len(err_tup) != 3:
            raise ValueError("Must exactly be 3 items:",err_tup)

        return {"item":err_tup[0],
                "type":err_tup[1],
                "reason":err_tup[2]}