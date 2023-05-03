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

from PySide2.QtWidgets import QApplication

from app_py.configs import config_obj
from app_py.configs import test_block
from app_py.editor import Editor as EditorObj
from app_py.viewer import Viewer as ViewerObj
from app_py.utilities import nodeUtils
from app_py.main import Main
from app_py.utilities import logUtils

log_file = os.path.join(config_obj.get("PATHS", "log_path"),
                        config_obj.get("DETAILS", "language"),
                        "{}.log".format(logUtils.timeStamp(), config_obj.get("DETAILS", "language"))
                        )

LOG = logUtils.getLogger(log_file)
logUtils.setLogLevel()
LOG.info("Starting...")


def setStrict(val=None):
    """
    Sets strict mode.

    **parameters**, **types**, **return** and **return types**

    :param val: Sets strict mode on or off.
    :type val: bool

    # >>> nagare.setStrict(True)

    """

    if val is None:
        val = "1"

    if val not in ("0", "1"):
        raise ValueError('DETAILS strict should be string "0" or "1".')

    config_obj.set("DETAILS", "strict", str(val))
    print("Strict error checking set to:", val)


def setPropagate(val=None):
    """
    Set the propagations switch for the datablock.

    **parameters**, **types**, **return** and **return types**

    :param val: Sets datablock propagation on or off.
    :type val: int

    # >>> nagare.setPropagate(True)

    """

    if val is None:
        val = "1"

    if val not in ["0", "1"]:
        raise ValueError('DETAILS propagate should be string "0" or "1".')

    config_obj.set("DETAILS", "propagate", str(val))
    print("Datablock propagation set to:", val)


def setLanguage(lang_str=None):
    """
    Use this to change the language to operate with beside Python.
    Also runs ``setup()`` once again to affect changes.

    **parameters**, **types**, **return** and **return types**

    :param lang_str: the language to be used. Valid: py, jsx, lua.
    :type lang_str: str

    # >>> nagare.setLanguage("jsx")

    """

    if lang_str is None:
        lang_str = "py"

    config_obj.set("DETAILS", "language", lang_str)

    modules_path = os.path.join(config_obj.get("PATHS", "root"),
                                "modules",
                                config_obj.get("DETAILS", "language"))
    config_obj.set("PATHS", [os.path.abspath(modules_path)])


class Editor(EditorObj):
    """
    Runs the editor, used for authoring graphs.

    **parameters**, **types**, **return** and **return types**

    :param software: the platform to be ran. Example: maya, ae, max.
    :type software: str

    :param language: the language to be used. Valid: py, jsx, lua.
    :type language: str

    :param datablock: Serializable datablock (ideally).
    :type datablock: dict

    # >>> nagare.Editor("maya", "py", datablock_dict)
    # >>> nagare.Editor("max", "py", self.data)
    # >>> nagare.Editor("ae", "jsx", datablock)
    # >>> nagare.Editor("fusion", "lua", datablock)

    """

    def __init__(self,
                 software=None,
                 language=None,
                 graph_file=None,
                 datablock=None):

        if software is None:
            software = "generic"

        if language is None:
            language = config_obj.get("DETAILS", "language")

        if graph_file is None:
            graph_file = config_obj.get("PATHS", "default_json")

        if datablock is None:
            datablock = test_block

        if language != config_obj.get("DETAILS", "language"):
            setLanguage(language)

        self._app = None
        if not QApplication.instance():
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        super(Editor, self).__init__(software,
                                     language,
                                     graph_file,
                                     datablock)
        self.ui.show()
        print("Editor", software, language, graph_file)

        self._app.exec_()
        # del self._app
        sys.exit(0)


class Player(Main):
    """
    Runs the player. Used for running graphs in Python env.
    Inherits Main, calls Viewer.

    **parameters**, **types**, **return** and **return types**

    :param json_file: Full path of JSON file.
    :type json_file: str

    :param datablock: Serializable datablock (ideally).
    :type datablock: dict

    # >>> nagare.Player(r"C:\tests\test_graph.json", datablock)
    # >>> nagare.Player(self.json_graph, self.datablock)

    """

    def __init__(self, json_file=None, datablock=None):
        if json_file is None:
            json_file = config_obj.get("PATHS", "default_json")

        if datablock is None:
            datablock = test_block

        self._app = None
        if not QApplication.instance():
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        super(Player, self).__init__()

        self.strict = int(config_obj.get("DETAILS", "strict"))
        self.propagate = int(config_obj.get("DETAILS", "propagate"))

        _copy_block = datablock.copy()
        self.player = ViewerObj(json_file)
        self.player.setWindowTitle(config_obj.get("DETAILS", "player_title"))
        self.player.log_btn.clicked.connect(self._openLog)
        self.player.scene.setMode("player")

        self.runJson(json_file, _copy_block)
        nodeUtils.postProcessNodes(self.player.scene, self.nodes_all)

        self.player.refresh()
        # self.player.scene.update()
        self.player.feedback("Ran: {}".format(json_file))

        self._app.exec_()
        # del self._app
        sys.exit(0)

    def _openLog(self):
        """
        Opens the log.txt file if self.log_file is a valid file in drive.
        """

        if os.path.isfile(self.log_file):
            if sys.platform == "win32":
                os.startfile(self.log_file)
            else:
                from subprocess import call as _sub_call
                _sub_call(["open", self.log_file])

            self.player.feedback("Opening log: {}".format(self.log_file))
        else:
            self.player.feedback("Log not found: {}".format(self.log_file))


class Viewer(Main):
    """
    Runs the Viewer.
    Inherits app_py, calls Viewer.
    Used only for displaying results from non-python apps.

    **parameters**, **types**, **return** and **return types**

    :param graph_json: Full path of JSON graph that was just ran.
    :type graph_json: str

    :param score_json: Full path of JSON score extracted from graph_json.
    :type score_json: str

    # >>> nagare.Viewer(r"C:\graphs\ae_build.json", r"C:\score.json")

    """

    def __init__(self, graph_json, score_json):
        for _json_file in (graph_json, score_json):
            if not os.path.exists(_json_file):
                raise IOError("Not found: {}".format(_json_file))

        self._app = None
        if not QApplication.instance():
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        super(Viewer, self).__init__()

        self.player = ViewerObj(graph_json)
        _score_data = self.getDataFromJson(score_json)

        for _score in _score_data:
            _node_obj = nodeUtils.getObject(_score, self.player.scene)

            if not _node_obj:
                raise RuntimeError("Failed to find node pointer:",
                                   _score["name"],
                                   _score["uuid"])

            _msg = "\n".join(_score["messages"])
            _node_obj.setErrors(_score.get("errors", list()))

            if _score["error"]:
                _node_obj.setDirty(state="error", message=_msg)
            elif _score["skip"]:
                _node_obj.setDirty(state="skip", message=_msg)
            else:
                _node_obj.setDirty()

        self._app.exec_()
        # del self._app
        sys.exit(0)


if __name__ == "__main__":
    # config_obj.set("PATHS", "mod_paths", [r"C:\repo\_dummy\basic", r"C:\repo\_dummy\custom", r"C:\repo\_dummy\basic"])
    # config_obj.set("PATHS", "mod_paths", [r"C:\repo\_dummy_jsx"])
    # Editor(language="jsx", graph_file="C:/repo/nagare/graphs/xxx.json")
    # Editor(graph_file=r"C:/repo/nagare/graphs/xxx.json")
    Editor()
    # Player()
    # Viewer(r"C:/repo/nagare/graphs/tester_jsx.json", r"C:\repo\_tmp\batman.json")
