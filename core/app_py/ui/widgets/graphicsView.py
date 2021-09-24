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

from PySide2.QtCore import (Qt,
                            QPoint)

from itemNode import Spawn as itemNode
from PySide2.QtWidgets import QGraphicsView


class Spawn(QGraphicsView):
    """
    Creates an instance of QGraphicsView with reimplemented functions.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Object pointer of QGraphicsScene instance.
    :type scene_obj: object

    :return: If strict is set to True, recursion will stop on Error.
    :rtype: None

    - Example::

        graphicsView(self.scene_obj)
    """

    def __init__(self,scene_obj):
        super(Spawn,self).__init__()
        self.scene_obj = scene_obj

        self.__drag = False
        self.__pressed = False
        self.__zoom = 1.0

        self.setObjectName("graphicsView")
        frame_css = "QGraphicsView#graphicsView {background-color: rgb(42,42,42);}"

        self.setStyleSheet(frame_css)
        self.setScene(self.scene_obj)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)


    def zoomExtents(self):
        """
        Fits the view to the bounding boxes of its items.
        """

        self.fitInView(self.scene_obj.itemsBoundingRect(),
                       Qt.KeepAspectRatio)


    def wheelEvent(self,event):
        """
        :meta private:
        """

        inFactor = 1.25
        outFactor = 1/inFactor
        oldPos = self.mapToScene(event.pos())

        if event.delta() > 0:
            zoom_value = inFactor
        else:
            zoom_value = outFactor

        self.scale(zoom_value,zoom_value)
        newPos = self.mapToScene(event.pos())
        _delta = newPos-oldPos
        self.__zoom = zoom_value
        self.translate(_delta.x(),_delta.y())


    def mouseMoveEvent(self,event):
        """
        :meta private:
        """

        if self.__drag:
            _delta = (self.mapToScene(event.pos()) -\
                      self.mapToScene(self.__prevPos))*-1.0

            _center = QPoint(self.viewport().width()/2+_delta.x(),
                             self.viewport().height()/2+_delta.y())

            _new_center = self.mapToScene(_center)
            self.centerOn(_new_center)
            self.__prevPos = event.pos()
            return

        if self.__pressed:
            for _nd in self.scene_obj.items():
                if not type(_nd) is itemNode:
                    continue

                if _nd.isSelected:
                    _nd.drawMe()
        try:
            super(Spawn,self).mouseMoveEvent(event)
        except:
            pass


    def mousePressEvent(self,event):
        """
        :meta private:
        """

        self.__pressed = True

        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.__drag = True
            self.__prevPos = event.pos()
            self.setCursor(Qt.OpenHandCursor)
        elif event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)

        super(Spawn,self).mousePressEvent(event)


    def mouseReleaseEvent(self,event):
        """
        :meta private:
        """

        self.__pressed = False

        if self.__drag:
            self.__drag = False
            self.setCursor(Qt.ArrowCursor)

        super(Spawn,self).mouseReleaseEvent(event)