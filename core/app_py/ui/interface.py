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

from __future__ import division
from __future__ import print_function

import os

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QMenu,
                               QAction,
                               QDialog,
                               QMenuBar,
                               QLineEdit,
                               QHBoxLayout,
                               QVBoxLayout,
                               QTreeWidget,
                               QSystemTrayIcon)
from widgets import icons
import widgets


class Spawn(QDialog):
    """
    Class to be called for Spawn, it uses PySide2.
    The widgets are found under widgets which you load into this.

    :param parent: description
    :type parent: object parent's object pointer

    """

    def __init__(self,parent=None):
        super(Spawn,self).__init__(parent)

        self.winW = 1200
        self.winH = 600

        self.file_menu = None
        self.graph_menu = None
        self.help_menu = None
        self._build()

        self.setStyleSheet(os.environ["NAGARE_GLOBAL_CSS"])


    def _build(self):
        """
        Builds the UI and repositions widgets.
        """

        # menu
        self.main_menu = QMenuBar()
        self.file_menu = self.main_menu.addMenu("File")
        self.graph_menu = self.main_menu.addMenu("Graph")
        self.help_menu = self.main_menu.addMenu("Help")

        self.strict_check = QAction(self)
        self.strict_check.setText("Stop on Error")
        self.strict_check.setCheckable(True)

        self.propagate_check = QAction(self)
        self.propagate_check.setText("Propagate Datablock")
        self.propagate_check.setCheckable(True)
        self.propagate_check.setChecked(True)

        self.file_menu.addAction("Open")
        self.file_menu.addAction("Save")
        self.file_menu.addAction(self.strict_check)
        self.file_menu.addAction(self.propagate_check)
        self.graph_menu.addAction("Run")
        self.graph_menu.addAction("Align (Selected)")
        self.graph_menu.addAction("Align (All)")
        self.graph_menu.addAction("Reset")
        self.graph_menu.addAction("Clear")
        self.help_menu.addAction("Help")
        self.help_menu.addAction("About")

        _main_layout = QHBoxLayout(self)
        _main_layout.setMenuBar(self.main_menu)

        self.scene = widgets.graphicsScene()
        self.view = widgets.graphicsView(self.scene)
        self.view.setSceneRect(100,50,self.winW,self.winH)
        _central_layout = QVBoxLayout()

        # top
        _top_layout = QHBoxLayout(self)

        # file IO buttons
        self.open_btn = widgets.buttonTool(self._getIcon("open.png"),
                                           "Open",
                                           _top_layout)

        self.save_btn = widgets.buttonTool(self._getIcon("save.png"),
                                           "Save",
                                           _top_layout)

        # playing button
        widgets.separator(False,_top_layout)

        self.strict_icon1 = self._getIcon("next.png")
        self.strict_icon2 = self._getIcon("stop.png")

        self.strict_btn = widgets.buttonTool(self.strict_icon1,
                                             "Stop on Error",
                                             _top_layout)

        self.propagate_icon1 = self._getIcon("tree.png")
        self.propagate_icon2 = self._getIcon("branch.png")

        self.propagate_btn = widgets.buttonTool(self.propagate_icon1,
                                                "Propagate Datablock",
                                                _top_layout)

        # graph buttons
        widgets.separator(False,_top_layout)

        self.zoom_btn = widgets.buttonTool(self._getIcon("zoom.png"),
                                           "Zoom Extents",
                                           _top_layout)

        self.align_btn = widgets.buttonTool(self._getIcon("align.png"),
                                            "Align",
                                            _top_layout)

        self.group_btn = widgets.buttonTool(self._getIcon("group.png"),
                                            "Group Selected Nodes",
                                            _top_layout)

        self.reset_btn = widgets.buttonTool(self._getIcon("reset.png"),
                                            "Reset",
                                            _top_layout)

        self.clear_btn = widgets.buttonTool(self._getIcon("clear.png"),
                                            "Clear",
                                            _top_layout)

        # search
        self.find_txt = QLineEdit()
        self.find_txt.setToolTip("Search node by name.")
        _top_layout.addWidget(self.find_txt)

        self.erase_btn = widgets.buttonTool(self._getIcon("erase.png"),
                                            "Clear search field",
                                            _top_layout)

        _central_layout.addLayout(_top_layout)

        # graph
        _central_layout.addWidget(self.view)
        _main_layout.addLayout(_central_layout)

        # bottom
        _bottom_layout = QHBoxLayout(self)
        _central_layout.addLayout(_bottom_layout)

        # run buttons
        self.run_btn = widgets.buttonTool(self._getIcon("run.png"),
                                          "Run graph",
                                          _bottom_layout)

        # feedback
        self.info_txt = QLineEdit("Ready...")
        self.info_txt.setToolTip("Feedback")
        self.info_txt.setEnabled(False)
        _bottom_layout.addWidget(self.info_txt)

        # log button
        self.log_btn = widgets.buttonTool(self._getIcon("log.png"),
                                          "Open log",
                                          _bottom_layout)

        # module tree
        self.module_tree = QTreeWidget()
        self.module_tree.setItemsExpandable(True)
        self.module_tree.setAnimated(True)
        self.module_tree.setFixedWidth(200)
        self.module_tree.setHeaderLabels(["Modules:"])
        _main_layout.addWidget(self.module_tree)

        _win_icon = self._getIcon("icon.png")
        self.setWindowIcon(_win_icon)

        _menu = QMenu()
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(_win_icon)
        self.tray.setContextMenu(_menu)
        self.tray.show()
        self.tray.setToolTip(os.environ["NAGARE_EDITOR_TITLE"])


    def _getIcon(self,icon_name,qrc=True):
        """
        Convenience method for getting .qrc resources or files.

        **parameters**, **types**, **return** and **return types**

        :param icon_name: Name (with extension) of icon.
        :type icon_name: str

        :param qrc: Return qrc or not.
        :type qrc: bool

        :return: Returns a QIcon pointer.
        :rtype: object

        - Example::

            self._getIcon("log.png",False)

        """

        if qrc:
            _icon_path = os.path.join(":",
                                      "icons",
                                      icon_name)
        else:
            _icon_path = os.path.join(os.environ["NAGARE_ICONS_PATH"],
                                      icon_name)
        return QIcon(_icon_path)