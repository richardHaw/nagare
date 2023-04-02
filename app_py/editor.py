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

from PySide2.QtCore import Qt
from PySide2.QtCore import Slot

from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QTreeWidgetItem

from ui.widgets import StartNode
from ui.widgets import ItemNode
from ui.widgets import GroupNode
from main import Main as pyApp
from ui.interface import Interface
from utilities import nodeUtils
from utilities import logUtils
from utilities import sceneUtils
from configs import config_obj
from configs import test_block


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

    def __init__(self, software, language, tree_json=None, data_block=None, parent=None):
        super(Editor, self).__init__()

        if tree_json is None:
            tree_json = config_obj.get("PATHS", "default_json")

        if data_block is None:
            data_block = dict()

        self.software = software
        self.language = language
        self.tree_json = tree_json
        self.data_block = data_block
        self.modules_root = config_obj.get("PATHS", "mod_paths")
        self.title_text = config_obj.get("DETAILS", "editor_title")
        self.starter = None
        self.log_dir = config_obj.get("PATHS", "log_path")
        self.logger_name = config_obj.get("DETAILS", "log_name")
        self.log_file = ""
        self.strict = False
        self.propagate = True

        self.ui = Interface(parent)

        for modulee_path in self.modules_root:
            if not os.path.exists(modulee_path):
                continue
            if modulee_path not in sys.path:
                sys.path.append(modulee_path)

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

        for _tm in (self.ui.file_menu, self.ui.graph_menu, self.ui.help_menu):
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

    def _triggerActions(self, _trigger_action):
        """
        Links menu items to their commands.
        """

        _trigger_text = _trigger_action.text()

        if _trigger_text == "Open":
            self._openTree()
        elif _trigger_text == "Save":
            self.saveTree()
        elif _trigger_text == "Stop on Error":
            self._setStrict()
        elif _trigger_text == "Propagate Datablock":
            self._setPropagate()
        elif _trigger_text == "Align (Selected)":
            self._alignTree(False)
        elif _trigger_text == "Align (All)":
            self._alignTree(True)
        elif _trigger_text == "Reset":
            self.buildTree()
        elif _trigger_text == "Clear":
            self.clearTree()
        elif _trigger_text == "Help":
            pass
        elif _trigger_text == "About":
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

        for mod_path in self.modules_root:
            print("Searching modules in {}".format(mod_path))
            if not os.path.isdir(mod_path):
                raise RuntimeError("No module path: ".format(mod_path))

        _branch_count = 1
        _branch_added = list()
        _leaf_added = list()

        for mod_path in self.modules_root:
            _mod_name = os.path.basename(mod_path)

            for _branch in os.listdir(mod_path):
                if _branch in _branch_added:
                    continue

                _branch_path = os.path.join(mod_path, _branch)

                if not os.path.isdir(_branch_path) or _branch.startswith("_"):
                    continue

                print(" {} ".format(_branch).center(88, "="))
                _branch_files = os.listdir(_branch_path)
                if len(_branch_files) < 1:
                    continue

                _branch_tit = "{}: {} ({})".format(str(_branch_count).zfill(2), _branch, _mod_name)
                _branch_obj = QTreeWidgetItem(self.ui.module_tree, [_branch_tit])
                _branch_obj.setExpanded(True)
                _branch_added.append(_branch)

                for _leaf_file in _branch_files:
                    _leaf_name = _leaf_file.split(".")[0]

                    if _leaf_file.startswith("_") or _leaf_name in _leaf_added:
                        continue
                    if _leaf_file.split(".")[-1] not in ext_map[self.language]:
                        continue

                    _leaf_obj = QTreeWidgetItem(_branch_obj, [_leaf_name])
                    _leaf_path = os.path.abspath(os.path.join(_branch, _leaf_file))

                    _leaf_obj.setToolTip(0, nodeUtils.getDescription(_leaf_path))
                    _leaf_obj.setWhatsThis(0, _leaf_path)
                    _branch_obj.addChild(_leaf_obj)
                    _leaf_added.append(_leaf_name)
                    print("- Loaded", _leaf_file)
                _branch_count += 1

        self.ui.module_tree.itemClicked.connect(self._clicker)
        self.ui.module_tree.setHeaderLabels(["{} Modules".format(self.software).title()])

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

        for _node in _all_nodes:
            _node.setSelected(True)

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
                                     "{}.log".format(logUtils.timeStamp(), self.software)
                                     )

        logger = logUtils.getLogger(self.logger_name, self.log_file)
        logger.propagate = True
        return logger

    def buildTree(self):
        """
        Builds the graph from the value stored in self.tree_json.
        IMPORTANT: copies self.data_block to starter
        Must be a valid JSON file.
        """

        _starter = sceneUtils.buildGraph(self.ui.scene, self.tree_json, self.data_block)
        if not isinstance(_starter, StartNode):
            self.clearTree()
            self._feedback(_starter, 2)
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
        _dummy = pyApp()
        _dummy.strict = self.strict
        _dummy.propagate = self.propagate
        _copy_block = self.data_block.copy()
        _dummy.runJson(self.tree_json, _copy_block)

        print("=" * 168)
        self.buildTree()

        for _node in _dummy.nodes_all:
            _dummy_dict = {"name": _node.name, "uuid": _node.uuid}
            _dummy_obj = nodeUtils.getObject(_dummy_dict, self.ui.scene)
            _msg = "\n".join(_node.messages)
            _dummy_obj.desc = _node.description
            _dummy_obj.setErrors(_node.getErrors())

            if _node.error:
                _dummy_obj.setDirty(state="error", msg=_msg)
            elif _node.skip:
                _dummy_obj.setDirty(state="skip", msg=_msg)
            else:
                _dummy_obj.setDirty()

            print("\n", "@", _msg)

        del(_dummy)
        self.ui.scene.update()
        self._feedback("Ran: {}".format(self.tree_json))

    def _groupSelected(self):
        """
        Groups all selected nodes.
        Must have more than 1 node_items selected.
        """

        _widgets = [s for s in sceneUtils.getSelected(self.ui.scene) if isinstance(s, ItemNode)]

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

        _selection = sceneUtils.getSelected(self.ui.scene)
        if not _selection:
            return

        _groups = [g for g in self.ui.scene.items() if isinstance(g, GroupNode)]

        if not is_all:
            for _selected in _selection:
                sceneUtils.alignTreeRecurse(_selected)
                sceneUtils.alignTreeRecurse(_selected)

            for _group in _groups:
                for _selected_item in _selection:
                    if _selected_item in _group.group_widgets:
                        _group.rebuildRect()
            return

        sceneUtils.alignTreeRecurse(self.starter)
        sceneUtils.alignTreeRecurse(self.starter)

        for _group in _groups:
            _group.rebuildRect()

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
        self.ui.info_txt.setText(str(feed_text))
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
    top_app = QApplication(sys.argv)

    hApp = Editor("generic",
                  config_obj.get("DETAILS", "language"),
                  data_block=test_block)

    hApp.show()
    top_app.exec_()
    sys.exit(0)
