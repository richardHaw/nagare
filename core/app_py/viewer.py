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

from PySide2.QtGui import QIcon

from PySide2.QtWidgets import (QMenu,
                               QDialog,
                               QLineEdit,
                               QHBoxLayout,
                               QVBoxLayout,
                               QSystemTrayIcon)

from ui import widgets
from ui.widgets import icons
from utilities import sceneUtils


class Spawn(QDialog):
    """
    **parameters**, **types**, **return** and **return types**

    :param json_file: Full path of JSON file.
    :type json_file: str

    :param datablock: Serializable datablock (ideally).
    :type datablock: dict

    """

    def __str__(self):
        return __name__


    def __init__(self,json_file,datablock=None):
        super(Spawn,self).__init__()
        self.json_file = json_file
        self.datablock = datablock

        self.winW = 1200
        self.winH = 600

        self._setup()
        self.setStyleSheet(os.environ["NAGARE_GLOBAL_CSS"])

        if self.json_file:
            if not os.path.isfile(self.json_file):
                raise IOError("JSON file not found:",self.json_file)
            self.build(self.json_file,self.datablock)

        self.show()


    def _setup(self):
        """
        Creates and arranges the elements.
        """

        self.setWindowTitle(os.environ["NAGARE_VIEWER_TITLE"])

        #top
        _main_layout = QVBoxLayout(self)

        self.scene = widgets.graphicsScene()
        self.scene.setMode("viewer")
        self.view = widgets.graphicsView(self.scene)
        self.view.setSceneRect(100,50,self.winW,self.winH)
        _main_layout.addWidget(self.view)

        #bottom
        widgets.separator(True,_main_layout)
        _bottom_layout = QHBoxLayout(self)
        _main_layout.addLayout(_bottom_layout)

        self.info_txt = QLineEdit("Ready...")
        self.info_txt.setToolTip("Feedback")
        self.info_txt.setEnabled(False)
        _bottom_layout.addWidget(self.info_txt)

        _log_icon = QIcon(os.path.join(":",
                                       "icons",
                                       "log.png"))

        self.log_btn = widgets.buttonTool(_log_icon,
                                          "Open log",
                                          _bottom_layout)

        _win_icon = QIcon(os.path.join(":",
                                       "icons",
                                       "icon.png"))

        self.setWindowIcon(_win_icon)

        _menu = QMenu()
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(_win_icon)
        self.tray.setContextMenu(_menu)
        self.tray.show()
        self.tray.setToolTip(os.environ["NAGARE_VIEWER_TITLE"])


    def build(self,json_file,datablock=None):
        """
        **parameters**, **types**, **return** and **return types**

        :param json_file: Full path of JSON file.
        :type json_file: str

        :param datablock: Serializable datablock (ideally).
        :type datablock: dict

        """

        _b = sceneUtils.buildGraph(self.scene,json_file,datablock)
        if isinstance(_b,str) or _b is None:
            self.scene.resetToStarter()
            print("Failed to build tree.")
            return


    def feedback(self,msg):
        """
        Updates the feedback text.

        **parameters**, **types**, **return** and **return types**

        :param msg: The message text.
        :type msg: str

        """

        self.info_txt.setText(msg)


    def notify(self,title,msg):
        """
        Show a notification on the tray.

        **parameters**, **types**, **return** and **return types**

        :param title: The title text.
        :type title: str

        :param msg: The message text.
        :type msg: str

        """

        self.tray.showMessage(title,msg)


    def refresh(self):
        """
        Updates the scene.
        """

        self.scene.update()


if __name__ == "__main__":
    from PySide2.QtWidgets import QApplication

    top_app = QApplication(sys.argv)
    tester = Spawn(os.environ["NAGARE_DEFAULT_JSON"])

    top_app.exec_()
    sys.exit(0)