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
from datetime import datetime

from PySide2.QtCore import (Qt,
                            QRect,
                            QPointF)

from PySide2.QtGui import (QPen,
                           QBrush,
                           QColor,
                           QPainter,
                           QTransform,
                           QPainterPath)

from PySide2.QtWidgets import QGraphicsEllipseItem
from .wireNode import Spawn as wireNode


class Spawn(QGraphicsEllipseItem):
    """
    Spawn for wire connection, to be parented to nodes.
    You can only have 1 connection for "in" type sockets.
    Multiple connections are allowed for "out" type sockets.

    **parameters**, **types**, **return** and **return types**

    :param parent: Object pointer of this widget.
    :type parent: object

    :param socketType: Indicates if this is an "in" or "out" socket.
    :type socketType: str

    - Example::

        socket_slot(self,"out")
    """

    def __str__(self):
        return __name__

    def __init__(self, parent, socketType):
        self.parent = parent
        self.socketType = socketType
        super(Spawn, self).__init__(self.parent)

        self.hovered = False
        self.new_line = None
        self.out_wires = []
        self.in_wire = None
        self._item_under = None

        self._setup()

    def _setup(self):
        """
        Creates and arranges the elements.
        """

        self.setAcceptHoverEvents(True)

        _socket_size = 20
        _socket_center = _socket_size * 0.5
        _socket_color = QColor(240, 180, 0)

        self.bg_brush = QBrush()
        self.bg_brush.setStyle(Qt.SolidPattern)
        self.bg_brush.setColor(_socket_color)

        self.sel_brush_color = QColor(255, 120, 180)
        self.sel_brush = QBrush()
        self.sel_brush.setStyle(Qt.SolidPattern)
        self.sel_brush.setColor(self.sel_brush_color)

        self.pen_color = QColor(20, 20, 20)
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(self.pen_color)

        self.selPen_color = QColor(0, 50, 50)
        self.selPen = QPen()
        self.selPen.setStyle(Qt.SolidLine)
        self.selPen.setWidth(1)
        self.selPen.setColor(self.selPen_color)

        _socket_posX = -_socket_center
        _socket_posY = 35

        if self.socketType == "out":
            if "widgets.itemNode" in self.parent.__str__():
                _socket_posX = self.parent.width - _socket_center
            elif "widgets.startNode" in self.parent.__str__():
                _socket_posX = self.parent.width - _socket_center
                _socket_posY = self.parent.width * 0.5 - _socket_center

        self.rect = QRect(int(_socket_posX),
                          int(_socket_posY),
                          int(_socket_size),
                          int(_socket_size))

    def shape(self):
        """
        :meta private:
        """

        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        """
        :meta private:
        """

        return QRect(self.rect)

    def paint(self, painter, option, widget):
        """
        :meta private:
        """

        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing |
                               QPainter.SmoothPixmapTransform |
                               QPainter.HighQualityAntialiasing,
                               True)

        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)

        if self.hovered:
            painter.setBrush(self.sel_brush)
        else:
            painter.setBrush(self.bg_brush)

        painter.drawEllipse(self.rect)

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

    def mousePressEvent(self, event):
        """
        :meta private:
        """

        if not self.scene().editable:
            return

        self._item_under = None

        if self.socketType == "out":
            rect = self.boundingRect()

            pointA = QPointF(rect.x()+rect.width() / 2,
                             rect.y()+rect.height() / 2)

            pointA = self.mapToScene(pointA)
            pointB = self.mapToScene(event.pos())

            self.new_line = wireNode(pointA, pointB)
            self.out_wires.append(self.new_line)
            self.scene().addItem(self.new_line)
        else:
            super(Spawn, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        :meta private:
        """

        if not self.scene().editable:
            return

        self._item_under = self.scene().itemAt(event.scenePos().toPoint(), QTransform())

        if self.socketType == "out":
            pointB = self.mapToScene(event.pos())
            self.new_line.pointB = pointB
            return

        super(Spawn, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        :meta private:
        """

        _under_type = self._item_under.socketType
        if not type(self._item_under) is Spawn:
            self.killWire(self.new_line)
            print(datetime.now(), "Dropped under a non-socket.")
            return

        if _under_type == "out":
            self.killWire(self.new_line)
            print(datetime.now(), "Dropped under an out-socket.")
            return

        if _under_type == "in":
            _in = self._item_under.parentItem().plug_in.in_wire
            if _in:
                self.killWire(_in)
                print(datetime.now(), "Killed old wire.", _in)

        if self.socketType == "out" and _under_type == "in":
            Spawn.connectWire(self.new_line, self, self._item_under)
            print(datetime.now(), "Connected new wire.")

            if not self._item_under.parentItem().node_in:
                raise RuntimeError("Connection failed!")

        super(Spawn, self).mouseReleaseEvent(event)

    def getCenter(self):
        """
        Call this to get the center coordinates of the socket.
        """

        rect = self.boundingRect()
        center = QPointF(rect.x() + rect.width() * 0.5, rect.y() + rect.height() * 0.5)
        center = self.mapToScene(center)
        return center

    def killWire(self, kill_this_wire):
        """
        Call this to kill a wire connected to this socket.

        **parameters**, **types**, **return** and **return types**

        :param kill_this_wire: Object pointer of the wire to be deleted.
        :type kill_this_wire: object

        - Example::

            socketNode.killWire(self.wire_to_kill)
        """

        if kill_this_wire in self.out_wires:
            self.out_wires.remove(kill_this_wire)

        self.scene().removeItem(kill_this_wire)
        print(kill_this_wire)
        print(datetime.now(), "Remove wire from scene", kill_this_wire)

        self.in_wire = None

    def _setParentNodeIn(self, node_to):
        """
        :meta private:
        """

        node_info = node_to.getInfoDict()
        self.parentItem().node_in = node_info

    def _setParentNodeOut(self, node_to):
        """
        :meta private:
        """

        node_info = node_to.getInfoDict()
        parent_node = self.parent

        if node_info not in parent_node.nodes_out:
            parent_node.nodes_out.append(node_info)

    def _isNodeItem(self, node_pointer):
        """
        :meta private:
        """

        _node_type = str(type(node_pointer))

        if "widgets.itemNode" not in _node_type and "widgets.startNode" not in _node_type:
            raise TypeError("Not a node item ({}): {}".format(_node_type, node_pointer))

        return node_pointer

    @staticmethod
    def connectWire(wire_obj, connect_from, connect_to):
        """
        Sets up wire connections and setup in/out connection info.

        **parameters**, **types**, **return** and **return types**

        :param wire_obj: Object pointer of the wire to be connected.
        :type wire_obj: object

        :param connect_from: Object pointer of the source socket node.
        :type connect_from: object

        :param connect_to: Object pointer of the target socket node.
        :type connect_to: object

        :return: None
        :rtype: NoneType

        - Example::

            socketNode.connectWire(self.new_line,self,self._item_under)
        """

        if not wire_obj.scene().editable:
            return

        wire_obj.source = connect_from
        wire_obj.target = connect_to
        old_wire = connect_to.parentItem().plug_in.in_wire
        connect_to.parentItem().plug_in.in_wire = wire_obj
        connect_to.parentItem().node_in = connect_from.parentItem()
        wire_obj.pointB = connect_to.getCenter()

        # put here for now
        connect_to._setParentNodeIn(connect_from.parent)
        connect_from._setParentNodeOut(connect_to.parent)

        if not old_wire:
            return

        if old_wire in old_wire.source.out_wires:
            old_wire.source.out_wires.remove(old_wire)
