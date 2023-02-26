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

from PySide2.QtGui import (QPen,
                           QColor,
                           QPainter,
                           QTransform,
                           QPainterPath)

from PySide2.QtCore import (Qt,
                            QPointF)

from PySide2.QtWidgets import QGraphicsPathItem


class Spawn(QGraphicsPathItem):
    """
    Spawn connecting nodes to each other.
    Created by "pulling" a socket.
    Remove a wire by pulling and dropping it on something that's not a socketNode instance.

    **parameters**, **types**, **return** and **return types**

    :param pointA: QPointF pointer of the starting point, defaults to 0.0,0.0.
    :type pointA: object

    :param pointB: QPointF pointer of the ending point, defaults to 50.0,50.0.
    :type pointB: object

    :return: None
    :rtype: NoneType

    - Example::

        _a = self.mapToScene(QPointF(88.0,168.0)
        _b = self.mapToScene(event.pos())

        self.new_line = wireNode(_a,_b)
    """

    _defaultA = QPointF(0.0, 0.0)
    _defaultB = QPointF(50.0, 50.0)


    def __str__(self):
        return __name__


    def __init__(self,pointA=_defaultA,pointB=_defaultB):
        super(Spawn, self).__init__()

        self._pointA = pointA
        self._pointB = pointB
        self._source = None
        self._target = None

        self._setup()

    def _setup(self):
        """
        Setup the look of the widget.
        """

        self.setZValue(-1)
        self.setBrush(Qt.NoBrush)

        __pen_color = QColor("#ffa500")
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(__pen_color)
        self.setPen(self.pen)

    def mousePressEvent(self, event):
        """
        :meta private:
        """

        if not self.scene().editable:
            return

        self.old_target = self.target
        self.pointB = event.pos()

    def mouseMoveEvent(self, event):
        """
        :meta private:
        """

        if not self.scene().editable:
            return

        self.pointB = event.pos()

    def mouseReleaseEvent(self, event):
        """
        :meta private:
        """

        if not self.scene().editable:
            return

        _to_socket = self.scene().itemAt(event.scenePos().toPoint(), QTransform())

        if "socketNode" not in str(type(_to_socket)):
            self.pointB = self.target.getCenter()

            Spawn.removeFromSocket(self.scene(), self, self.old_target)
            return

        if _to_socket.in_wire:
            _old_wire = _to_socket.parentItem().plug_in.in_wire
            Spawn.removeFromSocket(self.scene(), _old_wire, _to_socket)

        self.old_target.parentItem().plug_in.in_wire = None
        self.target = _to_socket
        self.pointB = _to_socket.getCenter()
        _to_socket.parentItem().plug_in.in_wire = self

    @staticmethod
    def removeFromSocket(scene_item, line_item, socket_out):
        """
        Removes the wire from the scene and socket.

        **parameters**, **types**, **return** and **return types**

        :param scene_item: Object pointer of a QGraphicsScene instance.
        :type scene_item: object

        :param line_item: Object pointer of a wireNode instance.
        :type line_item: object

        :param socket_out: Object pointer of a socketNode instance.
        :type socket_out: object

        :return: None
        :rtype: NoneType

        - Example::

            Spawn.removeFromSocket(self.scene(),
                                   self.wire_obj,
                                   self.socket_out)

        """

        _node_to = socket_out.parent
        _node_from = line_item.source.parent

        _node_to.plug_in.in_wire = None
        line_item.target = None

        _nfo = {"name": _node_to.name,
                "uuid": _node_to.uuid}

        if _nfo in _node_from.nodes_out:
            _node_from.nodes_out.remove(_nfo)

        if line_item in _node_to.plug_in.out_wires:
            _node_to.plug_in.out_wires.remove(line_item)

        scene_item.removeItem(line_item)

    def _updatePath(self):
        """
        Updates the wire's source and target.
        """

        path = QPainterPath()
        path.moveTo(self.pointA)

        dx = self.pointB.x() - self.pointA.x()
        dy = self.pointB.y() - self.pointA.y()

        ctrl1 = QPointF(self.pointA.x() + dx * 0.25,
                        self.pointA.y() + dy * 0.1)

        ctrl2 = QPointF(self.pointA.x() + dx * 0.75,
                        self.pointA.y() + dy * 0.9)

        path.cubicTo(ctrl1, ctrl2, self.pointB)
        self.setPath(path)

    def paint(self, painter, option, widget):
        """
        :meta private:
        """

        painter.setRenderHints(QPainter.Antialiasing|
                               QPainter.TextAntialiasing|
                               QPainter.SmoothPixmapTransform|
                               QPainter.HighQualityAntialiasing,
                               True)

        painter.setPen(self.pen)
        painter.drawPath(self.path())

    @property
    def pointA(self):
        """
        :meta private:
        """

        return self._pointA

    @pointA.setter
    def pointA(self, point):
        """
        :meta private:
        """

        self._pointA = point
        self._updatePath()

    @property
    def pointB(self):
        """
        :meta private:
        """

        return self._pointB

    @pointB.setter
    def pointB(self, point):
        """
        :meta private:
        """

        self._pointB = point
        self._updatePath()

    @property
    def source(self):
        """
        :meta private:
        """

        return self._source

    @source.setter
    def source(self, widget):
        """
        :meta private:
        """

        self._source = widget

    @property
    def target(self):
        """
        :meta private:
        """

        return self._target

    @target.setter
    def target(self, widget):
        """
        :meta private:
        """

        self._target = widget
