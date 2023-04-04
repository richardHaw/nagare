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
from __future__ import unicode_literals

import os
import sys
import uuid
import logging

from PySide2.QtWidgets import QApplication
from app_py.ui import widgets
from app_py.configs import config_obj

LOGGER = logging.getLogger(config_obj.get("DETAILS", "log_name"))
LOGGER.propagate = True


def getDescription(mod_path):
    """
    Looks for a txt file with the same name as the module.
    The txt file should be in a directory called "descriptions".

    **parameters**, **types**, **return** and **return types**

    :param mod_path: Full path of "modules" folder.
    :type mod_path: str

    :param folder_name: Folder name of the software or platform.
    :type folder_name: str

    :param module_name: File name of the .py, .jsx, .lua file module.
    :type module_name: str

    :return: The contents of the txt file. (if any).
    :rtype: str

    - Example::

        getDescription(r"C:\nagare\modules","maya2018","saveFile")

    :notes: Keep the description simple.
    """

    _desc = mod_path
    module_name = os.path.basename(mod_path).split(".")[0]
    _desc_path = os.path.join(os.path.dirname(mod_path), "descriptions", "{}.txt".format(module_name))

    if not os.path.exists(_desc_path):
        return _desc

    with open(_desc_path) as f:
        _desc = "\n".join(f.readlines())

    return _desc.strip("\n")


def getIconPath(mod_path):
    """
    Looks for a png file with the same name as the module.
    The png file should be in a directory called "icons".
    Make a "_default.png" under icons to make a branch default icon.
    Returns a default icon if nothing is found.

    **parameters**, **types**, **return** and **return types**

    :param mod_path: Full path of "modules" folder.
    :type mod_path: str

    :param folder_name: Folder name of the software or platform.
    :type folder_name: str

    :param module_name: File name of the .py, .jsx, .lua file module.
    :type module_name: str

    :return: The contents of the txt file. (if any).
    :rtype: str

    - Example::

        getIconPath(r"C:\nagare\modules","maya2018","saveFile")

    :notes: Keep the icon's size small, ideally height should be 32px.
    """

    mod_parent = os.path.dirname(mod_path)
    module_name = os.path.basename(mod_path).split(".")[0]

    _icon_path = os.path.join(mod_parent, "icons", "{}.png".format(module_name))
    _branch_path = os.path.join(mod_parent, "icons", "_default.png")

    for _icn in (_icon_path, _branch_path, config_obj.get("PATHS", "default_icon")):
        if os.path.exists(_icn):
            return _icn

    print("No icons found.")


def getObject(node_data, scene_obj):
    """
    Used to get a object using its name and uuid.
    Will search a scene's items (ALL).

    **parameters**, **types**, **return** and **return types**

    :param node_data: A dict containing keys ["name"] and ["uuid"].
    :type node_data: dict

    :param scene_obj: The pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: The node's pointer, if found.
    :rtype: object

    :return: None, if this failed to find a node.
    :rtype: NoneType
    """

    all_nodes = [i for i in scene_obj.items() if type(i) in [widgets.ItemNode, widgets.StartNode]]
    for nd in all_nodes:
        if nd.name != node_data["name"]:
            continue

        # TO-DO UUID is a bit buggy for now
        nd_uuid = node_data["uuid"]

        if sys.version_info[0] > 2:
            bad_t = not isinstance(nd_uuid, str)\
                    and not isinstance(nd_uuid, uuid.UUID)
        else:
            bad_t = not isinstance(nd_uuid, str)\
                    and not isinstance(nd_uuid, unicode)\
                    and not isinstance(nd_uuid, uuid.UUID)

        if bad_t:
            raise TypeError("Not a str, unicode or uuid.UUID", nd_uuid, type(nd_uuid))

        if not isinstance(nd_uuid, uuid.UUID):
            nd_uuid = uuid.UUID(nd_uuid)

        if str(nd.uuid) == str(nd_uuid):
            return nd


def refresh(node_obj):
    """
    Used to force a refresh of a node.

    **parameters**, **types**, **return** and **return types**

    :param node_obj: Spawn to update.
    :type node_obj: object

    :return: None
    :rtype: NoneType
    """

    QApplication.processEvents()
    node_obj.scene.update()


def printTree(node_obj):
    """
    Method to print out a node's.
    Use this to run the graph or save it.
    This can be set to recursive.

    When a module is executed this method will catch its return value.

    - A dict means that running the node was successful.

    - None means a failed evaluation.

    - "skip" (str) means recursion won't resume to this node's children.

    **parameters**, **types**, **return** and **return types**

    :param node_obj: Starting node to operate from.
    :type node_obj: object

    :return: Returns a dict containing the node's information.
    :rtype: dict

    :return: If strict is set to True, recursion will stop on Error.
    :rtype: None

    - Example::

        printTree(next_node,True)

    :notes:

    Set the node object to Starter node to parse all.
    This WILL NOT parse nodes that are not connected by wire.
    """

    # sleep(0.01)
    print("printTree:", node_obj.name)

    out_dict = dict()
    out_dict["name"] = node_obj.name
    out_dict["class"] = ".".join(node_obj.__str__().split(".")[-2:])
    out_dict["icon"] = node_obj.icon_path
    out_dict["description"] = node_obj.description
    out_dict["command"] = node_obj.command
    out_dict["x"] = node_obj.posX
    out_dict["y"] = node_obj.posY
    out_dict["uuid"] = str(node_obj.uuid)
    out_dict["out_nodes"] = list()
    out_dict["in_node"] = node_obj.node_in

    # get in-nodes if itemNode
    if isinstance(node_obj, widgets.ItemNode):
        if node_obj.node_in:
            out_dict["in_node"] = node_obj.node_in

    # to uuid
    if out_dict["in_node"]:
        tmp_id = out_dict["in_node"].get("uuid")
        if isinstance(tmp_id, uuid.UUID):
            out_dict["in_node"]["uuid"] = str(tmp_id)

    # run out-nodes
    for nd_out in node_obj.nodes_out:
        next_node = getObject(nd_out, node_obj.scene)
        if not next_node:
            e = " - Out-node not found", nd_out.get("name", "")
            print(nd_out)
            print(e)
            raise AttributeError(e)

        out_dict["out_nodes"].append(printTree(next_node))

    LOGGER.info("Processed: {}".format(node_obj.name))
    return out_dict


def uniqueName(scene_obj, node_name):
    """
    Used for checking if a node with the same name exists.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :param node_name: Name of the node to be evaluated
    :type node_name: str

    :return: Returns True if node_name is unique.
    :rtype: bool

    - Example::

        uniqueName(self.scene,nodename):
    """

    for _nd in scene_obj.items():
        if "itemNode" not in _nd.__str__():
            continue

        if _nd.name == node_name:
            return False

    return True

def postProcessNodes(scene_obj, nodes_list):
    """

    """

    for _node in nodes_list:
        _dummy_dict = {"name": _node.name, "uuid": _node.uuid}
        _dummy_obj = getObject(_dummy_dict, scene_obj)
        _msg = "\n".join(_node.messages)
        _dummy_obj.description = _node.description
        _dummy_obj.setErrors(_node.getErrors())

        if _node.error:
            _dummy_obj.setDirty(state="error", msg=_msg)
        elif _node.skip:
            _dummy_obj.setDirty(state="skip", msg=_msg)
        else:
            _dummy_obj.setDirty()
