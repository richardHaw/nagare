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

import uuid
import json
from pprint import pprint

from PySide2.QtCore import Qt

from PySide2.QtGui import QPen
from PySide2.QtGui import QFont
from PySide2.QtGui import QColor
from PySide2.QtGui import QBrush
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPainterPath

from PySide2.QtWidgets import QGraphicsEllipseItem

from socketNode import SocketNode
from clickLabel import ClickLabel
from modalTextEdit import ModalTextEdit


class StartNode(QGraphicsEllipseItem):
    """
    Starter node, can only have 1 in the graph.
    Contains data_block in the form of a dict.
    Double-click to edit data_block, must be a valid dict (as string).
    The data_block is propagated down-stream from this node.
    There are no input sockets for this thing.

    **parameters**, **types**, **return** and **return types**

    :param name: Name of the node.
    :type name: str

    :param position_x: X position.
    :type position_x: int

    :param position_y: X position.
    :type position_y: int

    :param scene: The pointer of the QGraphicsScene parent item.
    :type scene: object

    - Example::

        startNode("Starter",10,20,self.scene,"Starter Spawn")
    """

    def __str__(self):
        return __name__

    def __init__(self, name, position_x=None, position_y=None, scene=None):
        if position_x is None:
            position_x = 0

        if position_y is None:
            position_y = 0

        super(StartNode, self).__init__()
        self.setAcceptHoverEvents(True)
        self.hovered = False

        self.name = name
        self.position_x = position_x
        self.position_y = position_y
        self.scene = scene
        self.description = "Starter Spawn"
        self.data_block = {}
        self.dirty_block = {}
        self.command = None
        self.uuid = uuid.uuid1()
        self.width = 120
        self.height = self.width
        self.error = False
        self.plug_out = None
        self.plug_in = None
        self.nodes_out = list()
        self.node_in = None
        self.label = None
        self.icon_path = None
        self.message = None

        self._setup()

        if self.scene is not None:
            self.scene.addItem(self)

        self.translate()

    def _setup(self):
        """
        Setups the colors and labels of the widget.
        """

        self.bg_color = QColor("#FFD300")
        self.bg_brush = QBrush(self.bg_color)

        self.sel_color = QColor("#F8E473")
        self.sel_brush = QBrush(self.sel_color)

        self.pen_default_color = QColor("#101010")
        self.pen_default = QPen(self.pen_default_color)
        self.pen_default.setWidthF(3.0)

        self.bg_selected = QColor("#F5F5F5")
        self.pen_selected = QPen(self.bg_selected)
        self.pen_selected.setWidthF(3.0)

        self.bg_hovered = QColor("#FFFFFF")
        self.pen_hovered = QPen(self.bg_hovered)
        self.pen_hovered.setWidthF(3.0)

        self.setRect(0, 0, self.width, self.width)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setToolTip(self.description)

        self.plug_out = SocketNode(self, "out")
        self.plug_in = None

        self.label = ClickLabel(self.name, self)
        self.label.setFont(QFont("Arial Black", 10))
        self.label.setDefaultTextColor(QColor("#000000"))

    def translate(self):
        """
        Retranslates the widget.
        """

        self.setX(self.position_x-self.width * 0.5)
        self.setY(self.position_y-self.width * 0.5)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """
        :meta private:
        """

        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing |
                               QPainter.SmoothPixmapTransform |
                               QPainter.HighQualityAntialiasing,
                               True)

        path_outline = QPainterPath()
        path_outline.addEllipse(-1, -1, self.width, self.width)
        painter.setBrush(Qt.NoBrush)

        if self.hovered:
            painter.setBrush(self.sel_brush)
            painter.setPen(self.pen_hovered)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setBrush(self.bg_brush)
            painter.setPen(self.pen_default if not self.isSelected() else self.pen_selected)
            painter.drawPath(path_outline.simplified())

    def drawMe(self):
        """
        Call this to update this object.
        """

        for line in self.plug_out.out_wires:
            if line.source:
                line.pointA = line.source.getCenter()

            if line.target:
                line.pointB = line.target.getCenter()

    def hoverEnterEvent(self, event):
        """
        :meta private:
        """

        QGraphicsEllipseItem.hoverEnterEvent(self, event)
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        """
        :meta private:
        """

        QGraphicsEllipseItem.hoverLeaveEvent(self, event)
        self.hovered = False
        self.update()

    def mouseMoveEvent(self, event):
        """
        :meta private:
        """

        if not self.scene.editable:
            return

        super(StartNode, self).mouseMoveEvent(event)

        for _view in self.scene.views():
            # if _view.zoom > 1.0:
                # _view.update()
            _view.update()

        self.drawMe()

    def mouseReleaseEvent(self, event):
        """
        :meta private:
        """

        super(StartNode, self).mouseReleaseEvent(event)
        event_position = event.pos()
        event_position = self.mapToScene(event_position)
        self.position_x = event_position.x()
        self.position_y = event_position.y()

    def mouseDoubleClickEvent(self, event):
        """
        :meta private:
        """

        try:
            _data = json.dumps(self.data_block)
        except TypeError:
            pprint(self.data_block)
            return

        new_data = ModalTextEdit(_data).closeCmd()

        try:
            out_dict = json.loads(new_data)
        except Exception as err:
            print(err)
            print("Failed to convert string to dict.")
            return

        if type(out_dict) is not dict or out_dict is None:
            print("Failed to turn data to type dict.")
            return

        if self.data_block == out_dict:
            return

        print("-" * 88)
        self.data_block = out_dict
        pprint(self.data_block)

    def setUUID(self, new_uuid):
        """
        uuid setter
        """

        self.uuid = uuid.UUID(new_uuid)

    def getInfoDict(self):
        """
        Return the minimum info to recreate a node:

        :return: hashable dict of basic info.
        :rtype: dict
        """

        return {"name": self.name, "uuid": self.uuid}
