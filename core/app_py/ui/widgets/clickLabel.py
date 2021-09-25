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

from PySide2.QtGui import (QFont,
                           QColor)

from PySide2.QtWidgets import QGraphicsTextItem
from .inputText import Spawn as inputText


class Spawn(QGraphicsTextItem):
    """
    Creates clickable text label widget.

    **parameters**, **types**, **return** and **return types**

    :param label_text: The text shown by the widget.
    :type label_text: str

    :param parent: Pointer of the parent widget.
    :type parent: object

    :param posiX: Offset X of the label.
    :type posiX: int

    :param posiY: Offset Y of the label.
    :type posiY: int

    - Example::

        clickLabel("text",self.scene)
    """

    def __init__(self,label_text,parent=None,posiX=5,posiY=0):
        self.label_text = label_text
        self.parent = parent
        self.posiX = posiX
        self.posiY = posiY

        super(Spawn,self).__init__(self.parent)
        self.initItem()


    def initItem(self):
        """
        Initial setup.
        """

        label_color = QColor("#FFFFFF")
        label_font = QFont("Ubuntu",10)

        self.setDefaultTextColor(label_color)
        self.setFont(label_font)
        self.setPlainText(self.label_text)
        self.setTextWidth(self.parent.width-2*4)

        self.reposition()


    def reposition(self):
        """
        Repositions the label widget relative to the parent's dimensions.
        """

        if not self.parent:
            return

        text_size = len(self.toPlainText())*5.5

        if "widgets.itemNode" in self.parent.__str__():
            self.setTextWidth(self.parent.width-2*4)
            self.setPos(self.posiX,self.posiY)
        elif "widgets.startNode" in self.parent.__str__():
            self.setTextWidth(self.parent.width-2*4)

            self.setPos(self.parent.width*0.5-text_size,
                        self.parent.width*0.5-20)
        elif "widgets.groupNode" in self.parent.__str__():
            self.setTextWidth(self.parent.width-2*2)

            self.setPos(self.parent.rect().x(),
                        self.parent.rect().y()-25)


    def mouseDoubleClickEvent(self,event):
        """
        :meta private:
        """

        _new_name = inputText("New name",
                              "Group Name").out()

        if not _new_name:
            return

        if _new_name == self.label_text:
            return

        self.label_text = _new_name
        self.setPlainText(self.label_text)

        if "widgets.groupNode" in self.parent.__str__():
            self.parent.name = _new_name