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
import ctypes

from random import randrange
from pprint import pprint

from PySide2.QtCore import (Qt,
                            Slot)

from PySide2.QtWidgets import (QAction,
                               QApplication,
                               QTreeWidgetItem)

from ui import StartNode
from ui import ItemNode
from ui import GroupNode
from .main import Main as app_py
from .ui.interface import Interface
from .utilities import (nodeUtils,
                        logUtils,
                        sceneUtils)


class Editor(object):
    """
    Runs the app.

    You feed it a Python dict that contains information for it to parse.

    Keep the dict simple, avoid putting pointers and complicated information.
    This will make it easier to debug your graph.

    Of course, you could enter a dict with complicated entries, too.
    The values and keys are mutable but avoid changing anything when possible.

    Keeping things simple is the key to using this system.

    **parameters**, **types**, **return** and **return types**

    :param software: the Software name, same name as module folder (maya,maya2018).
    :type software: str

    :param language: the language to be used. Valid: py, jsx, lua.
    :type language: str

    :param tree_json: Path of the graph JSON file saved from this app, r"C:/graphs/babalu.json".
    :type tree_json: str

    :param data_block: Dictionary containing the information to be parsed.
    :type data_block: dict

    :param parent: Parent object's pointer, to be used on interafce,too.
    :type parent: object

    :return: None
    :rtype: NoneType

    - Example::

        test_block = {"what" : "This is Hawdini",
                      "where" : "Made in Japan",
                      "when" : "On my spare time",
                      #"why" : "To make a better world", # <- to invoke an error
                      "who" : "Richard Haw"}

        top_app = QApplication(sys.argv)
        myEditor = Spawn("maya",data_block=test_block)
        myEditor.show()
        top_app.exec_()
        sys.exit(0)
    """

    def __init__(self,
                 software,
                 language,
                 tree_json=os.environ["NAGARE_DEFAULT_JSON"],
                 data_block=dict(),
                 parent=None):

        super(Editor, self).__init__()

        self.software = software
        self.language = language
        self.tree_json = tree_json
        self.data_block = data_block
        self.modules_root = os.environ["NAGARE_MOD_PATH"]
        self.title_text = os.environ["NAGARE_EDITOR_TITLE"]
        self.starter = None
        self.log_dir = os.environ["NAGARE_LOG_PATH"]
        self.logger_name = os.environ["NAGARE_LOG"]
        self.log_file = ""
        self.strict = False
        self.propagate = True

        self.ui = Interface(parent)

        if self.modules_root not in sys.path:
            sys.path.append(self.modules_root)

        self._initUi()

    def _initUi(self):
        """
        Setup UI and initiates state.
        """

        self._linkCommands()
        self._populateModuleTree()
        self.ui.setWindowTitle(self.title_text)
        self.ui.scene.setMode("editor")

        self.clearTree()

        if os.path.isfile(self.tree_json):
            self.buildTree()
        else:
            raise IOError("This is not a file: {}".format(self.tree_json))

        self.ui.view.fitInView(self.ui.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.starter = sceneUtils.getStarter(self.ui.scene)

    def _linkCommands(self):
        """
        Links the commands to their widgets.
        """

        for _tm in (self.ui.file_menu,
                    self.ui.graph_menu,
                    self.ui.help_menu):

            _tm.triggered[QAction].connect(self._triggerActions)

        self.ui.open_btn.clicked.connect(self._openTree)
        self.ui.run_btn.clicked.connect(self._playJson)
        self.ui.log_btn.clicked.connect(self.openLog)
        self.ui.save_btn.clicked.connect(self.saveTree)
        self.ui.strict_btn.clicked.connect(self._setStrict)
        self.ui.propagate_btn.clicked.connect(self._setPropagate)
        self.ui.group_btn.clicked.connect(self._groupSelected)
        self.ui.zoom_btn.clicked.connect(self._zoomExtents)
        self.ui.align_btn.clicked.connect(self._alignTree)
        self.ui.reset_btn.clicked.connect(self.buildTree)
        self.ui.clear_btn.clicked.connect(self.clearTree)
        self.ui.erase_btn.clicked.connect(self._clearSearch)
        self.ui.find_txt.textChanged[str].connect(self._searchTree)

    def _triggerActions(self, _ta):
        """
        Links menu items to their commands.
        """

        _tx = _ta.text()

        if _tx == "Open":
            self._openTree()
        elif _tx == "Save":
            self.saveTree()
        elif _tx == "Stop on Error":
            self._setStrict()
        elif _tx == "Propagate Datablock":
            self._setPropagate()
        elif _tx == "Align (Selected)":
            self._alignTree(False)
        elif _tx == "Align (All)":
            self._alignTree(True)
        elif _tx == "Reset":
            self.buildTree()
        elif _tx == "Clear":
            self.clearTree()
        elif _tx == "Help":
            pass
        elif _tx == "About":
            pass

    def _populateModuleTree(self):
        """
        Builds Nodes Tree Repository from "modules" folder contents.
        Default folder names are "custom", "basic" and "debug".

        Custom nodes can be made and stored under a folder that starts with the software name.

        - Example::

            software ("maya2018")

            custom nodes folder ("maya2018_ModelCheck")
        """

        ext_map = {"py": ["py", "pyc"],
                   "jsx": ["jsxbin", "jsxinc"]
                   }

        if not os.path.isdir(self.modules_root):
            raise IOError("No module path: ".format(self.modules_root))
        print("Searching modules in {}".format(self.modules_root))

        _cat_count = 1
        for _cat in os.listdir(self.modules_root):
            _cat_dir = os.path.join(self.modules_root, _cat)

            if not os.path.isdir(_cat_dir) or _cat.startswith("_"):
                continue

            _mfiles = os.listdir(_cat_dir)
            if len(_mfiles) < 1:
                continue

            print(" {} ".format(_cat).center(88, "="))
            _tree_tit = "{}: {} nodes".format(str(_cat_count).zfill(2), _cat)
            _branch = QTreeWidgetItem(self.ui.module_tree, [_tree_tit])
            _branch.setExpanded(True)
            _added = list()

            for _leaf_file in _mfiles:
                _leaf_name = _leaf_file.split(".")[0]
                _leaf_ext = _leaf_file.split(".")[-1]

                if _leaf_file.startswith("_") or _leaf_name in _added:
                    continue

                if _leaf_ext not in ext_map[self.language]:
                    continue
                
                _leaf_node = QTreeWidgetItem(_branch, [_leaf_name])
                _leaf_path = os.path.abspath(os.path.join(_cat_dir, _leaf_file))
                _leaf_tt = nodeUtils.getDescription(_leaf_path)

                _leaf_node.setToolTip(0, _leaf_tt)
                _leaf_node.setWhatsThis(0, _leaf_path)
                _branch.addChild(_leaf_node)
                _added.append(_leaf_name)
                print("- Loaded", _leaf_file)
            _cat_count += 1

        self.ui.module_tree.itemClicked.connect(self._clicker)
        _title = ["{} Modules".format(self.software).title()]
        self.ui.module_tree.setHeaderLabels(_title)

    def show(self):
        self.ui.show()

    def saveTree(self):
        """
        Saves the current graph to JSON, recursive.
        """

        _tj = sceneUtils.getGraph(os.path.dirname(self.tree_json), True)
        if not _tj:
            self._feedback("Cancelled...", 1)
            return

        _node_data = nodeUtils.printTree(self.starter)
        if len(_node_data.get("out_nodes")) < 1:
            pprint(_node_data)
            self._feedback("No nodes saved...", 2)
            self._alert("No nodes saved...", "Warning")
            return

        _out_data = {"nodes": _node_data, "groups": sceneUtils.getGroups(self.ui.scene)}
        sceneUtils.write(_tj, _out_data)
        self._setTree(_tj)
        self._feedback("Saved to: {}".format(self.tree_json))
        self._alert("Saved successfully...")

    def clearTree(self):
        """
        Clears the graph, leaving only the Starter Spawn with no data_block.
        """

        self.starter = self.ui.scene.resetToStarter()
        if self.starter is None:
            raise AssertionError("No starter found.")

        self._feedback("Cleared graph.", 1)

    def _openTree(self):
        """
        Opens a modal dialog so you could specify the JSON graph.
        Calls buildTree method to parse the JSON.
        """

        j_file = sceneUtils.getGraph(os.path.dirname(self.tree_json))
        if not j_file:
            return

        self._setTree(j_file)
        self._feedback("Opened graph: {}".format(j_file))

    def _setTree(self, json_path):
        if not os.path.isfile(json_path):
            self._feedback("Not found: {}".format(json_path), 2)
            self._alert("Invalid file...", "Warning")
            return

        self.tree_json = json_path
        self.buildTree()

    def _clearSearch(self):
        """
        Clears the search field.
        """

        self.ui.find_txt.setText("")
        sceneUtils.clearSelection(self.ui.scene)

    def _searchTree(self):
        """
        Searches the whole scene for matching names.
        """

        _pf = self.ui.find_txt.text()
        _all_nodes = sceneUtils.searchTree(self.ui.scene, _pf)
        sceneUtils.clearSelection(self.ui.scene)

        for _n in _all_nodes:
            _n.setSelected(True)

    def _setStrict(self):
        """
        Toggles the strict state of the scene.
        Will stop processing once it encounters a bad node.
        """

        self.strict = not self.strict
        self.ui.strict_check.setChecked(self.strict)

        if not self.strict:
            self.ui.strict_btn.setIcon(self.ui.strict_icon1)
            self._feedback("Will evaluate the graph even when there are Errors.", 1)
            return

        self.ui.strict_btn.setIcon(self.ui.strict_icon2)
        self._feedback("Stops evaluating the graph when there's an Error."), 1

    def _setPropagate(self):
        """
        Toggle datablock propagation or just localized to branches.
        The datablock will be global if propagate is turned on.
        """

        self.propagate = not self.propagate
        self.ui.propagate_check.setChecked(self.propagate)

        if self.propagate:
            self.ui.propagate_btn.setIcon(self.ui.propagate_icon1)
            self._feedback("Datablock is propagated on the whole graph.")
            return

        self.ui.propagate_btn.setIcon(self.ui.propagate_icon2)
        self._feedback("Datablock only propagated on branch-level.", 1)

    def openLog(self):
        """
        Opens the log.txt file if self.log_file is a valid file in drive.
        """

        if os.path.isfile(self.log_file):
            if sys.platform in "win32":
                os.startfile(self.log_file)
            else:
                from subprocess import call as _sub_call
                _sub_call(["open", self.log_file])

            self._feedback("Opening log: {}".format(self.log_file))
            return

        self._feedback("Log not found: {}".format(self.log_file), 2)
        self._alert("No logs found...")

    def setupLog(self):
        """
        Create a logger and setup its log file.
        """

        self.log_file = os.path.join(self.log_dir,
                                     self.software,
                                     "{}.log".format(logUtils.timeStamp(),
                                                     self.software))
        logger = logUtils.getLogger(self.logger_name, self.log_file)
        logger.propagate = True
        return logger

    def buildTree(self):
        """
        Builds the graph from the value stored in self.tree_json.
        IMPORTANT: copies self.data_block to starter
        Must be a valid JSON file.
        """

        _g = sceneUtils.buildGraph(self.ui.scene,
                                   self.tree_json,
                                   self.data_block)

        if not isinstance(_g, StartNode):
            self.clearTree()
            self._feedback(_g, 2)
            return

        self._feedback("Rebuilt graph: {}".format(self.tree_json))

    def _zoomExtents(self):
        """
        Zoom the view to object bounds.
        """

        self.ui.view.zoomExtents()

    def _playJson(self):
        """
        Plays self.tree_json for debug purposes.
        """

        self.setupLog()
        _dummy = app_py()
        _dummy.strict = self.strict
        _dummy.propagate = self.propagate
        _copy_block = self.data_block.copy()
        _dummy.runJson(self.tree_json, _copy_block)

        print("=" * 168)
        self.buildTree()

        for _n in _dummy.nodes_all:
            _dummy_dict = {"name": _n.name,
                           "uuid": _n.uuid}

            _d = nodeUtils.getPointer(_dummy_dict,
                                      self.ui.scene)
            _m = "\n".join(_n.messages)
            _d.desc = _n.description
            _d.setErrors(_n.getErrors())

            if _n.error:
                _d.setDirty(state="error", msg=_m)
            elif _n.skip:
                _d.setDirty(state="skip", msg=_m)
            else:
                _d.setDirty()

            print("\n", "@", _m)

        del(_dummy)
        self.ui.scene.update()
        self._feedback("Ran: {}".format(self.tree_json))

    def _groupSelected(self):
        """
        Groups all selected nodes.
        Must have more than 1 node_items selected.
        """

        _widgets = [_s for _s in sceneUtils.getSelected(self.ui.scene) if isinstance(_s, ItemNode)]

        if len(_widgets) < 2:
            self._feedback("Select more than 1 node to group...", 1)
            self._alert("Selected more nodes...", "Nagare Alert")
            return

        GroupNode(self.ui.scene, _widgets)
        self._feedback("Grouped {} nodes...".format(len(_widgets)))

    def _alignTree(self, is_all=False):
        """
        Arranges down-stream nodes from first selection.
        Called 2x to prevent overlaps.
        Also aranges groups.

        **parameters**, **types**, **return** and **return types**

        :param name: Set to align all or selected. Defaults to False.
        :type name: bool
        """

        _sels = sceneUtils.getSelected(self.ui.scene)

        if not _sels:
            return

        _gps = [g for g in self.ui.scene.items() if isinstance(g, GroupNode)]

        if not is_all:
            for _sl in _sels:
                sceneUtils.alignTreeRecurse(_sl)
                sceneUtils.alignTreeRecurse(_sl)

            for _g in _gps:
                for _s in _sels:
                    if _s in _g.group_widgets:
                        _g.rebuildRect()
            return

        sceneUtils.alignTreeRecurse(self.starter)
        sceneUtils.alignTreeRecurse(self.starter)

        for _g in _gps:
            _g.rebuildRect()

    def _feedback(self, feed_text, level=0):
        """
        Updates the _feedback text and prints "feed_text".

        **parameters**, **types**, **return** and **return types**

        :param feed_text: The text that you want to appear.
        :type feed_text: str
        """

        colors = ["background-color: slate; color: silver",
                  "background-color: #fdd835; color: black",
                  "background-color: #ff5252; color: black"]

        if level > len(colors):
            level = len(colors)

        print(feed_text)
        self.ui.info_txt.setText(feed_text)
        self.ui.info_txt.setStyleSheet(colors[level])

    def _notify(self, title, msg):
        """
        Show a notification on the tray.

        **parameters**, **types**, **return** and **return types**

        :param title: The title text.
        :type title: str

        :param msg: The message text.
        :type msg: str

        """

        self.ui.tray.showMessage(title, msg)

    def _alert(self, text, title="Nagare Alert", style=0):
        """
        0 : OK
        1 : OK | Cancel
        2 : Abort | Retry | Ignore
        3 : Yes | No | Cancel
        4 : Yes | No
        5 : Retry | Cancel 
        6 : Cancel | Try Again | Continue
        """

        if sys.version_info[0] > 2:
            return ctypes.windll.user32.MessageBoxW(0, text, title, style)

        return ctypes.windll.user32.MessageBoxA(0, text, title, style)

    @Slot(QTreeWidgetItem, int)
    def _clicker(self, tree_item, column):
        """
        Creates new nodes from the repository.
        Called when QTreeWidgetItem is clicked.
        Spawn names are unique.
        """

        _text = tree_item.text(column)
        if _text[0].isdigit():
            return

        _counter = 1
        _name = _text + str(_counter).zfill(2)

        while not nodeUtils.uniqueName(self.ui.scene, _name):
            _counter += 1
            _name = _text + str(_counter).zfill(2)

        _whats_this = tree_item.whatsThis(0)
        _desc = nodeUtils.getDescription(_whats_this)
        _icon = nodeUtils.getIconPath(_whats_this)

        new_node = ItemNode(_name,
                            self.ui.winW/2+randrange(-50, 50),
                            self.ui.winH/2+randrange(-50, 50),
                            self.ui.scene,
                            _desc)

        _fol_name = os.path.basename(os.path.dirname(_whats_this))
        new_node.command = "{}.{}".format(_fol_name, _text)
        new_node.changeIcon(_icon)
        self._feedback("Created: {}".format(_name))


if __name__ == "__main__":
    import config
    top_app = QApplication(sys.argv)

    hApp = Editor("generic",
                 os.environ["NAGARE_LANGUAGE"],
                 data_block=config.TEST_BLOCK)

    hApp.show()
    top_app.exec_()
    sys.exit(0)
