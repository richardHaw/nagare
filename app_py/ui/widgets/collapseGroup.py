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

from PySide2.QtWidgets import (QGroupBox)
from PySide2.QtCore import Qt


class CollapseGroup(QGroupBox):
    def __str__(self):
        return __name__

    def __init__(self, title_text, label_height=20):
        super(CollapseGroup, self).__init__()

        self.title_text = title_text

        self._title_formatted = ""
        self._label_height = label_height
        self._orig_height = self.height()

        self.newTitle(self.title_text)
        self.setFlat(True)
        self.setCheckable(True)
        self.setAlignment(Qt.AlignAbsolute)
        self.toggled.connect(self._resizer)

    def _resizer(self):
        _win = self.window()
        _win_width = _win.size().width()
        _win_height = _win.size().height()
        _new_height = 0

        if self.isChecked():
            self.setMaximumHeight(self._orig_height)
            _new_height = _win_height + (self._orig_height - self._label_height)
            self.newTitle("{} - ".format(self.title_text))
        else:
            self._orig_height = self.height()
            self.setMaximumHeight(self._label_height)
            self.newTitle("{} + ".format(self.title_text))
            _new_height = _win_height - (self._orig_height + self._label_height)

        _win.resize(_win_width, _new_height)

    def setLabelHeight(self, new_hgt):
        self._label_height = new_hgt
        self._resizer()

    def newTitle(self, new_title):
        self._title_formatted = "{} ".format(new_title)
        self.setTitle(self._title_formatted)
