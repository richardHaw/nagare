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

import uuid

from PySide2.QtCore import (Qt,
                            QRect)

from PySide2.QtGui import (QColor,
                           QBrush,
                           QPainter)

from PySide2.QtWidgets import QGraphicsScene

from itemNode import Spawn as itemNode
from startNode import Spawn as startNode
from groupNode import Spawn as groupNode


class Spawn(QGraphicsScene):
    """
    Creates an instance of QGraphicsScene with reimplemented functions.
    Takes no arguements.

    **parameters**, **types**, **return** and **return types**

    :return: If strict is set to True, recursion will stop on Error.
    :rtype: None

    - Example::

        graphicsScene()
    """

    def __init__(self,mode="editor"):
        super(Spawn,self).__init__()

        _grid_color = QColor(25,25,25,150)
        self.setBackgroundBrush(QBrush(_grid_color,
                                       Qt.CrossPattern))
        self.setMode(mode)


    def setMode(self,mode):
        _modes = ["editor","player","viewer"]
        if mode not in _modes:
            print("Valid modes: {}".format((",".join(_modes))))
            raise ValueError("Invalid mode: {}".format(mode))

        self.editable = mode == "editor"
        self.mode = mode;


    def keyPressEvent(self,event):
        """
        :meta private:
        """

        if not self.editable:
            return

        # delete selected
        if event.key() in (Qt.Key_Delete,Qt.Key_Backspace):
            for _w in self.selectedItems():
                if isinstance(_w,itemNode):
                    for _out_w in _w.plug_out.out_wires:
                        _w.scene.removeItem(_out_w)

                    _in_wire =_w.plug_in.in_wire
                    if _in_wire:
                        _in_wire.removeFromSocket(_w.scene,
                                                  _in_wire,
                                                  _in_wire.target)
                    _w.scene.removeItem(_w)
                elif isinstance(_w,groupNode):
                    _w.unparentChildren()
                    _w.scene.removeItem(_w)
                    self.clearSelection()

                    for _it in _w.group_widgets:
                        _it.setSelected(True)


    def resetToStarter(self):
        """
        Clears the scene.
        Creates a new starter node in the scene.

        :return: Pointer of the new starter node.
        :rtype: object
        """

        if not self.editable:
            return

        self.clear()
        _starter = startNode("Start",
                             self.sceneRect().width()/2,
                             self.sceneRect().height()/2,
                             self)
        _starter.uuid = uuid.uuid1()
        return _starter
