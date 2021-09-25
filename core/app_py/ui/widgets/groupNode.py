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
import random

from PySide2.QtGui import (QColor,
                           QBrush)

from PySide2.QtCore import QRectF
from PySide2.QtWidgets import QGraphicsRectItem
from .clickLabel import Spawn as clickLabel


class Spawn(QGraphicsRectItem):
    """
    Inherits QGraphicsRectItem, used to group nodes.
    Parents the listed nodes to this widget.

    **parameters**, **types**, **return** and **return types**

    :param scene: The pointer of the QGraphicsScene parent item.
    :type scene: object

    :param group_widgets: list of itemNode instances.
    :type group_widgets: list

    - Example::

        groupNode(self.scene,[widget_pointer1,widget_pointer2])
    """

    def __str__(self):
        return __name__


    def __init__(self,scene,group_widgets,name="New Group"):
        super(Spawn,self).__init__()

        self.scene = scene
        self.group_widgets = group_widgets
        self.name = name
        self._default_rgba = (160,200,200,150)
        self.label = None
        self.width = 0
        self.height = 0
        self.uuid = uuid.uuid1()

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.parentWidgetsList(self.group_widgets)
        self._setup()


    def _setup(self):
        """
        Final setup of widget.
        """

        self.rebuildRect()
        self.scene.addItem(self)
        self.setZValue(-2)

        self.setupBgColor(self._default_rgba)
        self.label = clickLabel(self.name,self)


    def mouseMoveEvent(self,event):
        """
        :meta private:
        """

        if not self.scene.editable:
            return

        super(Spawn,self).mouseMoveEvent(event)


    def parentWidgetsList(self,widgets_list):
        """
        Parents the node_items in widgets_list to this widget.

        **parameters**, **types**, **return** and **return types**

        :param widgets_list: list of itemNode instances.
        :type widgets_list: list

        """

        for _wd in widgets_list:
            _wd.setParentItem(self)


    def unparentChildren(self):
        """
        Unparents all children.
        """

        for _gp in self.group_widgets:
            _gp.setParentItem(None)
            _gp.drawMe()


    def setupBgColor(self,rgba_tuple):
        """
        Changes the color of the QGraphicsRectItem.

        **parameters**, **types**, **return** and **return types**

        :param rgba_tuple: tuple of RGBA values (255,255,255,255).
        :type rgba_tuple: tuple
        """

        _bg_color = QColor(*rgba_tuple)
        _bg_brush = QBrush(_bg_color)
        self.setBrush(_bg_brush)


    def rebuildRect(self):
        """
        Retranslates the rect and repositions the label.
        """

        self.custom_rect = Spawn.getBogusBBox(self.group_widgets)
        self.setRect(self.custom_rect)
        self.width = self.custom_rect.width()
        self.height = self.custom_rect.height()

        if self.label:
            self.label.reposition()


    @staticmethod
    def mergeRectsList(widgets_list):
        """
        Merges the bounding boxes of the node_items in widgets_list.

        **parameters**, **types**, **return** and **return types**

        :param widgets_list: list of itemNode instances.
        :type widgets_list: list

        :return: QRectF
        :rtype: QRectF
        """

        out = None
        _counter_max = len(widgets_list)
        _counter = 0

        while _counter != _counter_max:
            _wd1 = widgets_list[_counter]

            try:
                _wd2 = widgets_list[_counter+1]
            except IndexError:
                break

            _bbx1 = QRectF(_wd1.x(),
                           _wd1.y(),
                           _wd1.width,
                           _wd1.height)

            _bbx2 = QRectF(_wd2.x(),
                           _wd2.y(),
                           _wd2.width,
                           _wd2.height)

            out = _bbx1.united(_bbx2)
            _counter+=1

        return out


    @staticmethod
    def getBogusBBox(widgets_list):
        """
        Used for getting the selection bounding box.

        **parameters**, **types**, **return** and **return types**

        :param widgets_list: list of itemNode instances.
        :type widgets_list: list

        :return: QRectF
        :rtype: QRectF
        """

        _factor_x = 1.1
        _factor_y = 1.2

        widgets_list.sort(key = lambda wid: wid.x())
        _bogus_x = Spawn.mergeRectsList([widgets_list[0],
                                         widgets_list[-1]])

        widgets_list.sort(key = lambda wid: wid.y())
        _bogus_y = Spawn.mergeRectsList([widgets_list[0],
                                         widgets_list[-1]])

        _bogus_xy = _bogus_x.united(_bogus_y)

        _offset_w = _bogus_xy.width()*_factor_x
        _offset_h = _bogus_xy.height()*_factor_y
        _offset_x = (_offset_w-_bogus_xy.width())/2
        _offset_y = (_offset_h-_bogus_xy.height())/2

        _bogus_bb = QRectF(_bogus_xy.x()-_offset_x,
                           _bogus_xy.y()-_offset_y,
                           _offset_w,
                           _offset_h)
        # done
        return _bogus_bb