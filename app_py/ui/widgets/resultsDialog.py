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

import os

from PySide2.QtWidgets import (QLabel,
                               QDialog,
                               QLineEdit,
                               QSizePolicy,
                               QHeaderView,
                               QHBoxLayout,
                               QVBoxLayout,
                               QPushButton,
                               QSpacerItem,
                               QPlainTextEdit)
from PySide2.QtCore import Qt

from .tableModel import TableModel
from .tableView import TableView
from .collapseGroup import CollapseGroup
from app_py.configs import config_obj

GLOBAL_CSS = config_obj.get("DETAILS", "global_css")


class ResultsDialog(QDialog):
    def __str__(self):
        return __name__

    def __init__(self, node_name, status, desc="none", msg="", errors_list=[]):
        super(ResultsDialog, self).__init__()

        self.node_name = node_name
        self.errors_list = self._processErrors(errors_list)
        self.message = ""
        self.status = status
        self.headers = ["Item", "Type", "Reason"]
        self._desc = ""

        self._setup()
        self.setMessage(msg)
        self.setDesc(desc)
        self.resize(600, 800)
        self.setStyleSheet(GLOBAL_CSS)
        self.setModal(True)
        self.exec_()

    def _setup(self):
        self.setWindowTitle("{}'s details".format(self.node_name))
        _main_layout = QVBoxLayout()
        _main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(_main_layout)

        # information
        _info_box = CollapseGroup("Information:")
        _info_box.setCheckable(False)
        _info_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        _main_layout.addWidget(_info_box)

        _spec_layout = QVBoxLayout()
        _spec_layout.setAlignment(Qt.AlignTop)
        _info_box.setLayout(_spec_layout)

        # name
        _name_layout = QHBoxLayout()
        _spec_layout.addLayout(_name_layout)

        _name_lbl = QLabel("Node Name:")
        _name_lbl.setFixedWidth(85)
        _name_layout.addWidget(_name_lbl)

        self.name_txt = QLineEdit(self.node_name)
        self.name_txt.setToolTip("Change node name?")
        self.name_txt.setMinimumWidth(100)
        _name_layout.addWidget(self.name_txt)

        # source
        _module_layout = QHBoxLayout()
        _spec_layout.addLayout(_module_layout)

        _module_lbl = QLabel("Module Name:")
        _module_lbl.setFixedWidth(85)
        _module_layout.addWidget(_module_lbl)

        _module_txt = QLineEdit(self.node_name + ".py")
        _module_txt.setToolTip("Source absolute URI")
        _module_txt.setMinimumWidth(100)
        _module_layout.addWidget(_module_txt)

        # status
        _status_layout = QHBoxLayout()
        _spec_layout.addLayout(_status_layout)

        _status_lbl = QLabel("Node Status:")
        _status_lbl.setFixedWidth(85)
        _status_layout.addWidget(_status_lbl)

        self.status_txt = QLineEdit(self.status)
        self.status_txt.setToolTip("Current node status.")
        self.status_txt.setMinimumWidth(100)
        self.status_txt.setEnabled(False)
        _status_layout.addWidget(self.status_txt)

        _spacer1 = QSpacerItem(10, 0, vData=QSizePolicy.Minimum)
        _spec_layout.addItem(_spacer1)

        # description
        _desc_box = CollapseGroup("Description:")
        _desc_box.setChecked(False)
        _main_layout.addWidget(_desc_box)

        self._desc_txt = QPlainTextEdit(self)
        self._desc_txt.setEnabled(False)
        self._desc_txt.setMinimumWidth(150)

        _desc_layout = QVBoxLayout()
        _desc_layout.addWidget(self._desc_txt)
        _desc_box.setLayout(_desc_layout)

        # messages
        _memo_box = CollapseGroup("Messages:")
        _main_layout.addWidget(_memo_box)

        self._message_txt = QPlainTextEdit(self)
        self._message_txt.setEnabled(False)
        self._message_txt.setMinimumWidth(150)

        _memo_layout = QVBoxLayout()
        _memo_layout.addWidget(self._message_txt)
        _memo_box.setLayout(_memo_layout)

        # table
        _table_box = CollapseGroup("Errors:")
        _main_layout.addWidget(_table_box)

        self.tableModel = TableModel(self,
                                     self.errors_list,
                                     self.headers)

        self.tableView = TableView(self.tableModel)
        self.tableView.setMaximumHeight(300)
        _hori_head = self.tableView.horizontalHeader()
        _hori_head.setSectionResizeMode(0, QHeaderView.Fixed)
        _hori_head.setSectionResizeMode(1, QHeaderView.Fixed)
        _hori_head.setSectionResizeMode(2, QHeaderView.Stretch)

        _table_layout = QVBoxLayout()
        _table_layout.addWidget(self.tableView)
        _table_box.setLayout(_table_layout)

        # button
        _button_box = CollapseGroup("")
        _button_box.setFixedHeight(65)
        _button_box.setCheckable(False)
        _main_layout.addWidget(_button_box)

        _spacer2 = QSpacerItem(10, 0, vData=QSizePolicy.Minimum)
        _spacer3 = QSpacerItem(10, 0, vData=QSizePolicy.Minimum)

        self.button = QPushButton("Accept")
        self.button.clicked.connect(self.dummy)
        _main_layout.addWidget(self.button)

        _button_layout = QHBoxLayout()
        _button_layout.addItem(_spacer2)
        _button_layout.addWidget(self.button)
        _button_layout.addItem(_spacer3)
        _button_box.setLayout(_button_layout)

    def dummy(self):
        self.resize(self.size().width(), 0)

    def setMemo(self, text_lines):
        for t in text_lines:
            self._message_txt.insertPlainText(t)

    def setDesc(self, strings):
        self._desc = strings
        self._desc_txt.setPlainText(self._desc)

    def setMessage(self, msg_str):
        self.message = msg_str
        self._message_txt.setPlainText(self.message)

    def _processErrors(self, raw_errors):
        safe_errors = list()

        if len(raw_errors) < 1:
            return [("", "", "")]

        for e in raw_errors:
            _a = e.get("item", None)
            _b = e.get("type", "")
            _c = e.get("reason", "")

            if _a is None:
                raise KeyError("Item not specified in error")

            safe_errors.append((str(_a), str(_b), str(_c)))

        return safe_errors


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication
    top_app = QApplication(sys.argv)

    GLOBAL_CSS = "QDialog {background-color: pink} "
    GLOBAL_CSS += "QLineEdit {background-color: slate; color: silver; border: none} "
    GLOBAL_CSS += "QToolButton {background-color: dimgrey; border: none} "
    GLOBAL_CSS += "QToolButton::hover {background-color: slategrey; border: none} "
    GLOBAL_CSS += "QMenuBar {border: none} "
    GLOBAL_CSS += "QTreeWidget {background-color: #505050; color: silver; border: none} "
    GLOBAL_CSS += "QTreeWidget::item:hover {background-color:slategrey;} "
    GLOBAL_CSS += "QHeaderView::section {background-color: dimgrey; border: none} "
    GLOBAL_CSS += "QGroupBox::indicator:unchecked {image: url(icons/group_collapse_close.png);} "
    GLOBAL_CSS += "QGroupBox::indicator:checked {image: url(icons/group_collapse_open.png);} "

    errs = [{"item": "babalu_layer_longName", "type": "LayerItem", "reason": "Not found"},
            {"item": "baba_comp", "type": "CompItem", "reason": "Incomplete items, missing layers"},
            {"item": "baba_foot", "type": "FootageItem", "reason": "File not found"},
            {"item": "baba_folder", "type": "FolderItem",  "reason": "Japanese name, should be ASCII only"},
            ]

    sp = ResultsDialog("babalu", "error", "my description", "", errs)
    sys.exit(0)
