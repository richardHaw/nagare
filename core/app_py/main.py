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
import json
import importlib

from traceback import format_exc
from pprint import (pprint,pformat)
from .resultObj import Spawn as result_obj
from .nodeDummy import Spawn as node_dummy
from .utilities import logUtils


class Spawn(object):
    """
    This creates an app object for python.
    You use this for running Haw-dini with no UI.
    It could call a viewer object for you to view results.
    """

    def __init__(self):
        super(Spawn, self).__init__()
        self.nodes_all = list()
        self.strict = False
        self.propagate = True
        self.log_obj = None
        self.log_file = ""


    def runJson(self,json_path,data_block):
        """
        Call this to run a JSON file graph.
        You give it a dict to process information.

        **parameters**, **types**, **return** and **return types**

        :param json_path: Full file path of JSON file graph.
        :type json_path: str

        :param data_block: A dict containing serializable information.
        :type data_block: dict

        :return: None
        :rtype: NoneType

        - Example::

            test_block = {"what" : "This is Hawdini",
                          "where" : "Made in Japan",
                          "when" : "On my spare time",
                          #"why" : "To make a better world", # <- to invoke an error
                          "who" : "Richard Haw"}

            Spawn.runJson("C:/test/sample.json",test_block")
        """

        self.log_file = os.path.join(os.environ["NAGARE_LOG_PATH"],
                                     os.environ["NAGARE_LANGUAGE"],
                                     "{}.log".format(logUtils.timeStamp(),
                                                     os.environ["NAGARE_LANGUAGE"]))
        self.log_obj = logUtils.getLogger(os.environ["NAGARE_LOG"],
                                          self.log_file)
        self.log_obj.propagate = True

        self.log_obj.info("Running JSON: {}".format(json_path))
        self.nodes_all = list()
        _datas = Spawn.getDataFromJson(json_path)
        _nodes_data = _datas.get("nodes", _datas)
        self._recurser(_nodes_data, data_block)

        self.log_obj.info("Finished running JSON: {}".format(json_path))
        logUtils.kill(self.log_obj)
        self.log_obj = None


    def _recurser(self,node_data,data_block):
        """
        Recurses the next set of data.

        **parameters**, **types**, **return** and **return types**

        :param node_data: Data of the original node.
        :type node_data: dict

        :param data_block: The datablock to be processed.
        :type data_block: dict

        :return: Returns a dict containing the node's information.
        :rtype: dict

        :return: If strict is set to True, recursion will stop on Error.
        :rtype: None
        """

        # early recursion stop
        if self.strict and self._failedNodes():
            return

        _run_result = None
        self.log_obj.info("="*88)
        _dummy = node_dummy(node_data)

        # inject a new key for feedback
        self.log_obj.info("Running: {}".format(_dummy.name))
        _dummy.messages.append("{}'s report:".format(_dummy.name))

        # copy the data_block
        _copy_block = None
        if self.propagate:
            _copy_block = data_block
        else:
            _copy_block = data_block.copy()

        # if there's no commands (starter)
        if _dummy.command is None:
            for _dummy_dict in _dummy.out_nodes:
                self._recurser(_dummy_dict, _copy_block)
            # this method actually ends here
            return

        # recurse with commands
        _ex_msgs = ["No Exception message..."]

        try:
            _proc_mod = importlib.import_module(_dummy.command)
            _run_result = _proc_mod.main(_copy_block)
            del(_proc_mod)
        except Exception as err:
            self.log_obj.info("="*88)
            _err_msg = "Failed module: {}".format(_dummy.command)
            _err_for = str(format_exc())
            _ex_msgs = [_err_msg]
            _ex_msgs.append(_err_for)
            self.log_obj.error(_err_msg)
            self.log_obj.error(_err_for)
            self.log_obj.error("="*88)

        # used for safety
        if not "resultObj" in repr(_run_result)\
           and not isinstance(_run_result,dict)\
           and _run_result is None:

            _tp = "{} returned {}".format(_dummy.name,str(type(_run_result)))
            _run_result = result_obj("error")
            _run_result.addMessage(_tp)
            _run_result.addMessage(pformat(_copy_block,indent=4))
            _run_result.addMessage("Created new error instance.")
            for e in _ex_msgs:
                _run_result.addMessage(e)

        # after running, add to nodes
        self.nodes_all.append(_dummy)

        # used for failed or skip
        if "resultObj" in repr(_run_result):
            _dummy.messages += _run_result.getMessages()
            _dummy.setErrors(_run_result.getErrors())

            if _run_result.getStatus() == "error":
                _dummy.error = True
                self.log_obj.error("Error running: {}".format(_dummy.name))
                self.log_obj.error(pformat(_copy_block,indent=4))

                for d in _dummy.messages:
                    self.log_obj.error(d)

                if self.strict:
                    _dummy.messages.append("Operation stopped")
                    return
            elif _run_result.getStatus() == "skip":
                _dummy.skip = True
                _dummy.messages.append("Skipped")

                for w in _dummy.messages:
                    self.log_obj.warning(w)

            # don't run down-stream nodes
            return _dummy

        if not isinstance(_run_result,dict):
            raise TypeError("Escaped results filtering: {}".format(_dummy.name))

        # run out-nodes
        for _dd in _dummy.out_nodes:
            # out_conn is now redundant because of nodes_all, refactor this.
            out_conn = self._recurser(_dd, _copy_block)

        # done
        _dummy.messages.append("Success")
        return _dummy


    def _failedNodes(self):
        """
        Returns a list of any failed nodes that was calculated.

        :return: A list of any failed nodes.
        :rtype: list
        """

        _out = list()

        for _fail in self.nodes_all:
            if _fail.error:
                _out.append(_fail)

        return _out


    @staticmethod
    def getDataFromJson(json_file):
        out = None

        if not os.path.exists(json_file):
            raise IOError("File not found: {}".format(json_file))

        with open(json_file) as json_buffer:
            out = json.load(json_buffer)

        return out


if __name__ == "__main__":
    dummy = Spawn()
    dummy.runJson(os.environ["NAGARE_DEFAULT_JSON"],
                  os.environ["TEST_BLOCK"])