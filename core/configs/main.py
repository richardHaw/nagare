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
import sys

TEST_BLOCK = dict()


def setup():
    """
    **NAGARE_PYVER** - *The system's Python version.*

    **NAGARE_EDITOR_TITLE** - *The system's Python version.*

    **NAGARE_VIEWER_TITLE** - *The system's Python version.*

    **NAGARE_FRAMEWORK_ROOT** - *The framwork's root directory.*

    **NAGARE_ROOT** - *Haw-dini's root directory.*

    **NAGARE_MOD_PATH** - *Root directory for modules.*

    **NAGARE_LOG_PATH** - *Root directory for logging.*

    **NAGARE_DEFAULT_JSON** - *Full path of the default JSON graph.*

    **NAGARE_DEFAULT_ICON** - *Full path of the default node icon.*

    **NAGARE_ICONS_PATH** - *Root directory for the icons.*

    **NAGARE_GLOBAL_CSS** - *Default CSS style for the UI.*

    **NAGARE_LANGUAGE** - *language name.*

    **TEST_BLOCK** - *default datablock for testing.*

    **NAGARE_LOG** - *Default handler name.*

    >>> setup()

    """
    global TEST_BLOCK

    global_css = "QDialog {background-color: dimgrey} "
    global_css+="QLineEdit {background-color: slate; color: silver; border: none} "
    global_css+="QToolButton {background-color: dimgrey; border: none} "
    global_css+="QToolButton::hover {background-color: slategrey; border: none} "
    global_css+="QMenuBar {border: none} "
    global_css+="QTreeWidget {background-color: #505050; color: silver; border: none} "
    global_css+="QTreeWidget::item:hover {background-color:slategrey;} "
    global_css+="QHeaderView::section {background-color: dimgrey; border: none} "
    # global_css+="QGroupBox::indicator:unchecked {image: url(icons/group_collapse_close.png);} "
    # global_css+="QGroupBox::indicator:checked {image: url(icons/group_collapse_open.png);} "

    fw_root = os.path.dirname(os.path.dirname(__file__))
    nagare_root = os.path.dirname(fw_root)
    icons_root = os.path.join(fw_root,"app_py","ui","widgets","icons")
    title_template = "Nagare {} (Alpha, Python-{})"
    lang = "py"
    pyver = str(sys.version_info[0])
    test_json = os.path.join(nagare_root,"graphs","tester_{}.json".format(lang))
    # test_json = os.path.abspath(os.path.join(nagare_root,"core","new.json"))

    envs = [
            "NAGARE_FRAMEWORK_ROOT",
            "NAGARE_ROOT",
            "NAGARE_MOD_PATH",
            "NAGARE_LOG_PATH",
            "NAGARE_ICONS_PATH",
            "NAGARE_DEFAULT_ICON",
            "NAGARE_DEFAULT_JSON",
            "NAGARE_GLOBAL_CSS",
            "NAGARE_LANGUAGE",
            "NAGARE_STRICT",
            "NAGARE_PROPAGATE",
            "NAGARE_PYVER",
            "NAGARE_LOG",
            "NAGARE_EDITOR_TITLE",
            "NAGARE_VIEWER_TITLE",
            ]

    nulls = [
             fw_root, # NAGARE_FRAMEWORK_ROOT
             nagare_root, # NAGARE_ROOT
             os.path.abspath(os.path.join(nagare_root,"modules",lang)), # NAGARE_MOD_PATH
             os.path.abspath(os.path.join(nagare_root,"log")), # NAGARE_LOG_PATH
             icons_root, # NAGARE_ICONS_PATH
             os.path.join(icons_root,"node.png"), # NAGARE_DEFAULT_ICON
             test_json, # NAGARE_DEFAULT_JSON
             global_css, # NAGARE_GLOBAL_CSS
             lang, # NAGARE_LANGUAGE
             "1", # NAGARE_STRICT
             "1", # NAGARE_PROPAGATE
             pyver, # NAGARE_PYVER
             "nagare", # NAGARE_LOG
             title_template.format("Editor",pyver), # NAGARE_EDITOR_TITLE
             title_template.format("Viewer",pyver), # NAGARE_VIEWER_TITLE
             ]

    for e in envs:
        if not os.environ.get(e,None):
            os.environ[e] = nulls[envs.index(e)]

    # might be better at config or nagare's init
    TEST_BLOCK.update({"what" : "This is Hawdini",
                       "where" : "Made in Japan",
                       "when" : "On my spare time",
                       #"why" : "To make a better world",
                       "who" : "Richard Haw"})

    print("Configs initiated...")