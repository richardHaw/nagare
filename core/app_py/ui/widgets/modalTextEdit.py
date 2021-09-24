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

import sys
import json

from PySide2.QtWidgets import (QDialog,
                               QTextEdit,
                               QVBoxLayout,
                               QPushButton,
                               QApplication)


class Spawn(QDialog):
    """
    Creates a modal dialog with text box.
    You have to call this with closeCmd() to get something meaningful.

    **parameters**, **types**, **return** and **return types**

    :param text_data: Text to be put in the text box.
    :type text_data: str

    :return: Returns text as string from the text box.
    :rtype: str

    - Example::

        new_str = Spawn(_data).closeCmd()
    """

    def __str__(self):
        return __name__


    def __init__(self,text_data=""):
        super(Spawn,self).__init__()

        self.text_data = text_data

        self._build()
        self.text_edit.setPlainText(self.text_data)

        self.setModal(True)
        self.show()
        self.exec_()


    def _build(self):
        """
        Create and arrange the elements in the UI.
        """

        self.main_layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumWidth(400)
        self.text_edit.setMinimumHeight(400)
        self.button = QPushButton("Save Data Block Information")
        self.button.clicked.connect(self.closeCmd)

        self.main_layout.addWidget(self.text_edit)
        self.main_layout.addWidget(self.button)


    def closeCmd(self):
        """
        This has to be called together with this class to get something back.

        :return: Returns text as string from the text box.
        :rtype: str
        """

        self.accept()
        return self.text_edit.toPlainText()


if __name__ == "__main__":
    debug = True
    top_app = QApplication(sys.argv)
    ui = Text(None)
    top_app.exec_()
    sys.exit(0)