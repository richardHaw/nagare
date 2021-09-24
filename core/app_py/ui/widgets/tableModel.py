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

from PySide2.QtCore import Qt
from PySide2.QtCore import SIGNAL
from PySide2.QtCore import QAbstractTableModel


class Spawn(QAbstractTableModel):
    def __init__(self, parent_obj, items_list, headers, *args):
        QAbstractTableModel.__init__(self, parent_obj, *args)
        self.items_list = items_list
        self.headers = headers


    def rowCount(self, parent_obj):
        return len(self.items_list)


    def columnCount(self, parent_obj):
        if not len(self.items_list):
            return 1

        return len(self.items_list[0])


    def data(self, index, role):
        if not len(self.items_list):
            return None

        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.items_list[index.row()][index.column()]


    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[col]
        return None


    def sort(self, col, order):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.items_list = sorted(self.items_list,
                                 key=operator.itemgetter(col))

        if order == Qt.DescendingOrder:
            self.items_list.reverse()

        self.emit(SIGNAL("layoutChanged()"))
