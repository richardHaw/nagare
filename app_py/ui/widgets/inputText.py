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

from PySide2.QtWidgets import QInputDialog
from PySide2.QtWidgets import QLineEdit


class InputText(QInputDialog):
    """
    Creates a modal dialog with text field.

    **parameters**, **types**, **return** and **return types**

    :param show_text: Title label.
    :type show_text: str

    :param def_txt: Initial text.
    :type def_txt: str
    """

    def __init__(self, show_text=None, def_txt=None):
        if show_text is None:
            show_text = "Enter text"

        if def_txt is None:
            def_txt = ""

        super(InputText, self).__init__()

        self.show_text = show_text
        self.def_txt = def_txt

        self.text, self.ok = self.getText(self,
                                          "New value:",
                                          "{}:".format(self.show_text),
                                          QLineEdit.Normal,
                                          self.def_txt)

    def out(self):
        """
        Return whatever is in the text field.

        :return: Returns the text value.
        :rtype: None or string
        """

        if self.text and self.ok:
            return str(self.text)
        else:
            return
