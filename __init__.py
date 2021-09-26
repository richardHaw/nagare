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

print("Starting Nagare...")

import os
import sys

from PySide2.QtWidgets import QApplication

if sys.version_info[0] > 2:
    from .core import configs
    from .core.app_py.editor import Spawn as editor
    from .core.app_py.viewer import Spawn as viewer
    from .core.app_py.utilities import nodeUtils
    from .core.app_py.main import Spawn as app_py
else:
    from core import configs
    from core.app_py.editor import Spawn as editor
    from core.app_py.viewer import Spawn as viewer
    from core.app_py.utilities import nodeUtils
    from core.app_py.main import Spawn as app_py


def setDefaults():
    """
    Initiates config and sets the defaults.
    These are all environment variables.

    **NAGARE_PYVER** - *The system's Python version.*

    **NAGARE_EDITOR_TITLE** - *The system's Python version.*

    **NAGARE_VIEWER_TITLE** - *The system's Python version.*

    **NAGARE_FRAMEWORK_ROOT** - *The framwork's root directory.*

    **NAGARE_ROOT** - *Haw-dini's root directory.*

    **NAGARE_MOD_PATH** - *Root directory for modules.*

    **NAGARE_LOG_PATH** - *Root directory for logging.*

    **NAGARE_DEFAULT_JSON** - *Full path of the default JSON graph.*

    **NAGARE_DEFAULT_ICON** - *Full path of the default node icon.*

    **NAGARE_ICONS_PATH** - *Root directory for the icons.*

    **NAGARE_GLOBAL_CSS** - *Default CSS style for the UI.*

    **TEST_BLOCK** - *Default datablock for testing.*

    **STRICT** - *Strict mode.*

    **PROPAGATE** - *Propagate datablock information.*

    >>> nagare.setDefaults()

    """

    configs.setup()


def setStrict(val="1"):
    """
    Sets strict mode.

    **parameters**, **types**, **return** and **return types**

    :param val: Sets strict mode on or off.
    :type val: bool

    >>> nagare.setStrict(True)

    """

    if val not in ["0","1"]:
        raise ValueError('NAGARE_STRICT should be string "0" or "1".')

    os.environ["NAGARE_STRICT"] = str(val)
    print("Strict error checking set to:",val)


def setPropagate(val="1"):
    """
    Set the propagations switch for the datablock.

    **parameters**, **types**, **return** and **return types**

    :param val: Sets datablock propagation on or off.
    :type val: int

    >>> nagare.setPropagate(True)

    """

    if val not in ["0","1"]:
        raise ValueError('NAGARE_PROPAGATE should be string "0" or "1".')

    os.environ["NAGARE_PROPAGATE"] = str(val)
    print("Datablock propagation set to:",val)


def setLanguage(lang_str="py"):
    """
    Use this to change the language to operate with beside Python.
    Also runs ``setup()`` once again to affect changes.

    **parameters**, **types**, **return** and **return types**

    :param lang_str: the language to be used. Valid: py, jsx, lua.
    :type lang_str: str

    >>> nagare.setLanguage("jsx")

    """

    os.environ["NAGARE_LANGUAGE"] = lang_str

    NAGARE_MOD_PATH = os.path.join(os.environ["NAGARE_ROOT"],
                                   "modules",
                                   os.environ["NAGARE_LANGUAGE"])
    os.environ["NAGARE_MOD_PATH"] = os.path.abspath(NAGARE_MOD_PATH)


class Editor(editor):
    """
    Runs the editor, used for authoring graphs.

    **parameters**, **types**, **return** and **return types**

    :param software: the platform to be ran. Example: maya, ae, max.
    :type software: str

    :param language: the language to be used. Valid: py, jsx, lua.
    :type language: str

    :param datablock: Serializable datablock (ideally).
    :type datablock: dict

    >>> nagare.Editor("maya","py",datablock_dict)
    >>> nagare.Editor("max","py",self.data)
    >>> nagare.Editor("ae","jsx",datablock)
    >>> nagare.Editor("fusion","lua",datablock)

    """

    def __init__(self,
                 software="generic",
                 language=os.environ["NAGARE_LANGUAGE"],
                 graph_file=os.environ["NAGARE_DEFAULT_JSON"],
                 datablock=configs.TEST_BLOCK):

        if language != os.environ["NAGARE_LANGUAGE"]:
            setLanguage(language)

        self._app = None
        if not QApplication.instance():
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        super(Editor,self).__init__(software,
                                    language,
                                    graph_file,
                                    datablock)
        self.ui.show()
        print("Editor",software,language,graph_file)

        # done
        self._app.exec_()
        # del self._app
        sys.exit(0)


class Player(app_py):
    """
    Runs the player. Used for running graphs in Python env.
    Inherits app_py, calls viewer.

    **parameters**, **types**, **return** and **return types**

    :param json_file: Full path of JSON file.
    :type json_file: str

    :param datablock: Serializable datablock (ideally).
    :type datablock: dict

    >>> nagare.Player(r"C:\tests\test_graph.json", datablock)
    >>> nagare.Player(self.json_graph, self.datablock)

    """

    def __init__(self,
                 json_file=os.environ["NAGARE_DEFAULT_JSON"],
                 datablock=configs.TEST_BLOCK):

        self._app = None
        if not QApplication.instance():
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        super(Player,self).__init__()

        self.strict = eval(os.environ["NAGARE_STRICT"])
        self.propagate = eval(os.environ["NAGARE_PROPAGATE"])
        _copy_block = datablock.copy()
        self.runJson(json_file,_copy_block)
        self.player = viewer(json_file)
        self.player.log_btn.clicked.connect(self._openLog)

        for _n in self.nodes_all:
            _dummy_dict = {"name":_n.name,
                           "uuid":_n.uuid}

            _node = nodeUtils.getPointer(_dummy_dict,
                                         self.player.scene)
            _msg = "\n".join(_n.messages)
            _node.desc = _n.description
            _node.setErrors(_n.getErrors())

            if _n.error:
                _node.setDirty(state="error",msg=_msg)
            elif _n.skip:
                _node.setDirty(state="skip",msg=_msg)
            else:
                _node.setDirty()

        self.player.refresh()
        self.player.scene.setMode("player")
        self.player.feedback("Ran: {}".format(json_file))

        # done
        self._app.exec_()
        # del self._app
        sys.exit(0)


    def _openLog(self):
        """
        Opens the log.txt file if self.log_file is a valid file in drive.
        """

        if os.path.isfile(self.log_file):
            if sys.platform in "win32":
                os.startfile(self.log_file)
            else:
                from subprocess import call as _sub_call
                _sub_call(["open",self.log_file])

            self.player.feedback("Opening log: {}".format(self.log_file))
        else:
            self.player.feedback("Log not found: {}".format(self.log_file))


class Viewer(app_py):
    """
    Runs the viewer.
    Inherits app_py, calls viewer.
    Used only for displaying results from non-python apps.

    **parameters**, **types**, **return** and **return types**

    :param graph_json: Full path of JSON graph that was just ran.
    :type graph_json: str

    :param score_json: Full path of JSON score extracted from graph_json.
    :type score_json: str

    >>> nagare.Viewer(r"C:\graphs\ae_build.json", r"C:\score.json")

    """

    def __init__(self, graph_json,score_json):
        for j in (graph_json,score_json):
            if not os.path.exists(j):
                raise IOError("Not found: {}".format(j))

        self._app = None
        if not QApplication.instance():
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        super(Viewer,self).__init__()

        self.player = viewer(graph_json)
        _score_data = self.getDataFromJson(score_json)

        for _score in _score_data:
            _node = nodeUtils.getPointer(_score,self.player.scene)

            if not _node:
                raise RuntimeError("Failed to find node pointer:",
                                   _score["name"],
                                   _score["uuid"])

            _msg = "\n".join(_score["messages"])
            _node.setErrors(_score.get("errors",list()))

            if _score["error"]:
                _node.setDirty(state="error",msg=_msg)
            elif _score["skip"]:
                _node.setDirty(state="skip",msg=_msg)
            else:
                _node.setDirty()

        # done
        self._app.exec_()
        # del self._app
        sys.exit(0)


if __name__ == "__main__":
    os.environ["NAGARE_MOD_PATH"] = r"C:\repo\_dummy"
    print(os.getenv("NAGARE_MOD_PATH"))

    # Editor(language="jsx",graph_file="C:/repo/nagare/graphs/tester_jsx_backup.json")
    Editor(graph_file=r"C:/repo/nagare/graphs/xxx.json")
    # Player()
    # Viewer(r"C:/repo/nagare/graphs/tester_jsx.json",r"C:\repo\_tmp\batman.json")
    pass
