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
from PySide2.QtCore import Qt

from PySide2.QtGui import (QPen,
                           QColor,
                           QBrush,
                           QPainter,
                           QPainterPath)

from PySide2.QtWidgets import (QGraphicsRectItem,
                               QGraphicsTextItem,
                               QGraphicsPixmapItem)

from .resultsDialog import ResultsDialog
from .clickLabel import ClickLabel
from .socketNode import SocketNode


class ItemNode(QGraphicsRectItem):
    """
    Inherits QGraphicsRectItem, used to create nodes.
    Nodes contain information as data_bloc using dict.
    It uses uuid as unique ID.

    **parameters**, **types**, **return** and **return types**

    :param name: Name of the node.
    :type name: str

    :param posX: X position.
    :type posX: int

    :param posY: X position.
    :type posY: int

    :param scene: The pointer of the QGraphicsScene parent item.
    :type scene: object

    :param desc: Text description, defaults to def_desc if not set.
    :type desc: str

    - Example::

        itemNode("sample",10,20,self.scene,"Sample Spawn")
    """

    def_desc = "Short description of your widget"

    def __str__(self):
        return __name__

    def __init__(self,
                 name,
                 posX=0,
                 posY=0,
                 scene=None,
                 desc=def_desc,
                 uuid_str=None):

        super(ItemNode, self).__init__()

        self.setAcceptHoverEvents(True)
        self.hovered = False

        self.name = name
        self.posX = posX
        self.posY = posY
        self.scene = scene
        self.desc = desc
        self.data_block = dict()
        self.command = None
        self.width = 160
        self.height = 80
        self.uuid = uuid.uuid1()
        self.error = False
        self.dirty = False
        self.skip = False
        self.plug_out = None
        self.plug_in = None
        self.nodes_out = list()
        self.node_in = None
        self._errors_list = list()
        self.label = None
        self.state = "Ready"
        self.state_label = None
        self.icon = None
        self.icon_path = ""
        self.messages = list()

        if uuid_str is not None:
            self.setUUID(uuid_str)

        self._setup()

    def _setup(self):
        """
        Setups the look of the widget.
        """

        _bg_color = QColor("#404040")
        self.bg_brush = QBrush(_bg_color)

        _hover_color = QColor("#274651")
        self.sel_brush = QBrush(_hover_color)

        _err_color = QColor("#e12120")
        self.err_brush = QBrush(_err_color)

        _skip_color = QColor("#E1AD01")
        self.skip_brush = QBrush(_skip_color)

        _dirty_color = QColor("#2b5329")
        self.dirty_brush = QBrush(_dirty_color)

        _pen_default_color = QColor("#101010")
        self.pen_default = QPen(_pen_default_color)
        self.pen_default.setWidthF(3.0)

        _bg_selected = QColor("#FFFFFF")
        self.pen_selected = QPen(_bg_selected)
        self.pen_selected.setWidthF(3.0)

        _bg_hovered = QColor("#FFFFFF")
        self.pen_hovered = QPen(_bg_hovered)
        self.pen_hovered.setWidthF(3.0)

        self.setToolTip(self.desc)
        self.setRect(0, 0, self.width, self.height)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)

        self.plug_out = SocketNode(self, "out")
        self.plug_in = SocketNode(self, "in")
        self.label = ClickLabel(self.name, self)

        self.state_label = QGraphicsTextItem(self)
        self.state_label.setPlainText("")
        self.state_label.setDefaultTextColor(QColor("#FFFFFF"))
        self.state_label.setPos(self.width - 45, self.height - 25)

        self.icon = QGraphicsPixmapItem(self)
        self.icon.setPos(0, self.height - 25)

        if self.scene is not None:
            self.scene.addItem(self)

        self.translate()

    def translate(self):
        """
        :meta private:
        """

        self.setX(self.posX-self.width / 2)
        self.setY(self.posY-self.height / 2)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """
        :meta private:
        """

        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing |
                               QPainter.SmoothPixmapTransform |
                               QPainter.HighQualityAntialiasing,
                               True)

        _hover_brush = self.sel_brush
        _normal_brush = self.bg_brush
        _corn = 5

        _path_outline = QPainterPath()
        _path_outline.addRoundedRect(-1,
                                     -1,
                                     self.width + 2,
                                     self.height + 2,
                                     _corn,
                                     _corn)

        painter.setBrush(Qt.NoBrush)

        if self.error:
            _hover_brush = self.err_brush
            _normal_brush = self.err_brush
        elif self.dirty:
            _hover_brush = self.dirty_brush
            _normal_brush = self.dirty_brush
        elif self.skip:
            _hover_brush = self.skip_brush
            _normal_brush = self.skip_brush

        if self.hovered:
            painter.setBrush(_hover_brush)
            painter.setPen(self.pen_hovered)
            painter.drawPath(_path_outline.simplified())
        else:
            painter.setBrush(_normal_brush)
            painter.setPen(self.pen_default if not self.isSelected() else self.pen_selected)
            painter.drawPath(_path_outline.simplified())

    def changeIcon(self, icon_path):
        """
        Changes the icon and moves it according to bitmap size.

        **parameters**, **types**, **return** and **return types**

        :param icon_path: The full file path of the icon.
        :type icon_path: str
        """

        _qpm = self.icon.pixmap()
        _qpm.load(icon_path)
        _hgt = _qpm.size().height()
        self.icon.setPos(8, self.height - _hgt - 5)
        self.icon.setPixmap(_qpm)
        self.icon_path = icon_path

    def setClean(self):
        """
        Sets the node clean.
        """

        self.dirty = False
        self.error = False
        self.skip = False
        self.state_label.setPlainText("")
        self.messages = list()

    def setErrors(self, errors):
        self._errors_list = errors

    def getErrors(self):
        return self._errors_list

    def setUUID(self, new_uuid):
        """
        uuid setter
        """

        self.uuid = uuid.UUID(new_uuid)
        if not str(self.uuid) == new_uuid:
            raise AttributeError("Failed to set UUID: {}".format(self.name))

    def setDirty(self, state="", msg="Processed"):
        """
        Sets the node dirty, changes the tooltip.

        **parameters**, **types**, **return** and **return types**

        :param state: state of the node.
        :type state: str

        :param msg: error or any messages.
        :type msg: str
        """

        if state == "error":
            self.error = True
            self.state = "Failed"
        elif state == "skip":
            self.skip = True
            self.state = "Skip"
        else:
            self.dirty = True
            self.state = "Done"

        self.messages.append(msg)
        self.state_label.setPlainText(self.state)

        self.setToolTip("{}\n{}\n{}".format(self.desc,
                                            "=" * 36,
                                            "\n".join(self.messages)))

    def drawMe(self):
        """
        Call this to update this object.
        """

        for line in self.plug_out.out_wires:
            if line.source:
                line.pointA = line.source.getCenter()

            if line.target:
                line.pointB = line.target.getCenter()

        if self.plug_in.in_wire:
            _w = self.plug_in.in_wire

            if _w.source:
                _w.pointA = _w.source.getCenter()

            if _w.target:
                _w.pointB = _w.target.getCenter()

    def hoverEnterEvent(self, event):
        """
        :meta private:
        """

        QGraphicsRectItem.hoverEnterEvent(self, event)
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        """
        :meta private:
        """

        QGraphicsRectItem.hoverLeaveEvent(self, event)
        self.hovered = False
        self.update()

    def mouseMoveEvent(self, event):
        """
        :meta private:
        """

        if not self.scene.editable:
            return

        super(ItemNode, self).mouseMoveEvent(event)

        for _v in self.scene.views():
            _v.update()

        self.drawMe()

    def mouseReleaseEvent(self, event):
        """
        :meta private:
        """

        super(ItemNode, self).mouseReleaseEvent(event)

        posi = event.pos()
        posi = self.mapToScene(posi)
        self.posX = posi.x()
        self.posY = posi.y()

    def mouseDoubleClickEvent(self, event):
        """
        :meta private:
        """

        _dw = ResultsDialog(self.name,
                            self.state,
                            self.desc,
                            "\n".join(self.messages),
                            self._errors_list)

    def coveredBy(self):
        """
        Simple test to see if it is "obscured" after alignment.
        If another node shares exactly the same coordinates it returns True.

        :return: None if not "obscured".
        :rtype: NoneType

        :return: True if it shares the same coordinates with another node.
        :rtype: bool
        """

        for _ni in self.scene.items():
            if _ni == self:
                continue

            if "widgets.itemNode" not in _ni.__str__():
                continue

            if int(_ni.posX) == int(self.posX) and int(_ni.posY) == int(self.posY):
                return True
        return False

    def getInfoDict(self):
        """
        Return the minimum info to recreate a node:

        :return: hashable dict of basic info.
        :rtype: dict
        """

        out = {"name": self.name,
               "uuid": self.uuid}

        return out
