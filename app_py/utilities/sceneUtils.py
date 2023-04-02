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

import os
import uuid
import json

import nodeUtils
from ..ui import widgets
from app_py.configs import config_obj
from PySide2.QtWidgets import QFileDialog


def getGraph(folder_start, save=False):
    """
    Method for creating modal file dialog.
    Used to open or save JSON file graphs files.

    **parameters**, **types**, **return** and **return types**

    :param folder_start: Set the start folder for the dialog.
    :type folder_start: str examples r"C:/graphs"

    :param save: Sets the operation of the function, save or open.
    :type save: bool Defaults to file open, set to True to save.

    :return: JSON file path
    :rtype: str

    - Example::

        getGraph(r"C:/graphs",True)
    """

    _diag = QFileDialog.getOpenFileName

    if save:
        _diag = QFileDialog.getSaveFileName

    j_file, _ = _diag(QFileDialog(),
                      "Save/Open Flow Graph:",
                      folder_start,
                      "JSON (*.json)")

    if not save and not os.path.exists(j_file):
        return

    if not j_file.endswith(".json"):
        return

    return j_file


def buildGraph(scene_obj, json_file, data_block={}):
    """
    Builds a new graph on the scene object.
    WARNING: Copies the datablock to the starter node.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :param json_file: Valid path of a JSON file.
    :type json_file: str

    :param data_block: A dictionary containing info for parsing.
    :type data_block: dict

    :return: The pointer of the new starter node if successful.
    :rtype: object

    :return: Error message if failed.
    :rtype: str
    """

    scene_obj.clear()
    _nodes_data = None
    _json_data = readGraphJson(json_file)

    if not _json_data:
        return "Failed to read: {}".format(json_file)

    # nodes
    try:
        _nodes_data = _json_data.get("nodes", _json_data)
    except:
        return "No nodes data: {}".format(json_file)

    # create starter
    _starter = widgets.StartNode(_nodes_data["name"],
                                 _nodes_data["x"],
                                 _nodes_data["y"],
                                 scene_obj)
    _starter.setUUID(_nodes_data["uuid"])

    # rebuild starter out nodes
    _tmp_nodes = list()
    for _node in _nodes_data["out_nodes"]:
        _tmp_nfo = {"name": _node["name"],
                    "uuid": uuid.UUID(_node["uuid"])
                    }

        _tmp_nodes.append(_tmp_nfo)
    _starter.nodes_out = _tmp_nodes

    # creates a copy of the datablock for the starter
    if isinstance(data_block, dict) and data_block:
        _starter.data_block = data_block.copy()

    # build and link
    buildTreeRecurse(_nodes_data["out_nodes"], scene_obj)
    linkTreeRecurse(_nodes_data, scene_obj)

    # groups, if any
    _gp_data = _json_data.get("groups", list())
    for _gp in _gp_data:
        _gp_kids = list()
        _all_kids = _gp["children"]

        if len(_all_kids) < 2:
            print("Warning: skip group creation, not enough nodes.")
            continue

        for _c in (_all_kids):
            _npt = nodeUtils.getObject(_c, scene_obj)

            if not _npt:
                print("Warning: child not found ({}).".format(_c["name"]))
                continue

            _gp_kids.append(_npt)

        if len(_gp_kids) < 2:
            print("Warning: not enough nodes to make a group.")
            continue

        widgets.GroupNode(scene_obj,
                          _gp_kids,
                          _gp["name"])

    # finishing
    for _v in scene_obj.views():
        _v.zoomExtents()

    return _starter


def getSelected(scene_obj):
    """
    Method returning selected nodes from the scene object.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: A list of selected objects, [] if nothing is selected.
    :rtype: list

    - Example::

        getSelected(self.scene)
    """

    return scene_obj.selectedItems()


def getStarter(scene_obj):
    """
    Returns a scene's Starter node.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: Pointer object of Starter node.
    :rtype: object

    - Example::

        getStarter(self.scene)
    """

    start_node = None

    for _nd in scene_obj.items():
        if not type(_nd) == widgets.StartNode:
            continue

        start_node = _nd
        break

    return start_node


def searchTree(scene_obj, node_keyword):
    """
    Searches the scene and returns nodes that match.
    The keyword is not case-sensitive.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :param node_keyword: Prefix to be searched.
    :type node_keyword: str

    :return: A list of nodes that starts with node_keyword.
    :rtype: list

    - Example::

        searchTree(self.scene,"findThisPrefix")
    """

    _out = list()
    if not node_keyword:
        return _out

    for _nd in getNodes(scene_obj):
        if node_keyword.lower() in _nd.name.lower():
            _out.append(_nd)
    return _out


def setClean(scene_obj):
    """
    Sets all nodes in the scene back to their clean states.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: None
    :rtype: NoneType

    - Example::

        getNodes(self.scene)
    """

    for _nd in getNodes(scene_obj):
        _nd.setClean()

    scene_obj.update()


def clearSelection(scene_obj):
    """
    Unselect all nodes in the scene.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    - Example::

        clearSelection(self.scene)
    """

    for _nd in getNodes(scene_obj):
        _nd.setSelected(False)


def getNodes(scene_obj):
    """
    Returns all nodes of the scene object.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: A list of all nodes in the scene object.
    :rtype: list

    - Example::

        getNodes(self.scene)
    """

    return [n for n in scene_obj.items() if isinstance(n, widgets.ItemNode)]


def getGroups(scene_obj):
    """
    Returns all groups of the scene object.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: A list of all groups in the scene object.
    :rtype: list

    - Example::

        getGroups(self.scene)
    """

    _out = list()

    for _gp in scene_obj.items():
        if not isinstance(_gp, widgets.GroupNode):
            continue

        _gp_nfo = dict()
        _gp_rect = _gp.rect()

        _gp_nfo["name"] = _gp.name
        _gp_nfo["uuid"] = str(_gp.uuid)
        _gp_nfo["children"] = list()

        _gp_nfo["rect"] = {"x":_gp_rect.x(),
                           "y":_gp_rect.y(),
                           "w":_gp_rect.width(),
                           "h":_gp_rect.height()}

        for _c in _gp.group_widgets:
            _c_nfo = {"name": _c.name,
                      "uuid": str(_c.uuid)}
            _gp_nfo["children"].append(_c_nfo)

        _out.append(_gp_nfo)

    return _out


def getBadNodes(scene_obj):
    """
    Scans the scene and look for nodes with error attribute set to True.

    **parameters**, **types**, **return** and **return types**

    :param scene_obj: Pointer of a QGraphicsScene object.
    :type scene_obj: object

    :return: A list of nodes with error attribute set to True.
    :rtype: list

    - Example::

        _pp = getBadNodes(self.scene)

        for _n in _pp:
            print(_n.name)
    """

    _bads = list

    for _nd in getNodes(scene_obj):
        if _nd.error:
            print("An error occurred in {}".format(_nd.name))
            _bads.append(_nd)

    return _bads


def buildTreeRecurse(tree_list, scene_item):
    """
    Builds a tree from a starting list and the information stored there.

    **parameters**, **types**, **return** and **return types**

    :param tree_list: Data from tree dict with key ["out_nodes"]
    :type tree_list: list

    :param scene_item: Pointer of a QGraphicsScene object.
    :type scene_item: object

    :return: None
    :rtype: NoneType

    - Example::

        buildTreeRecurse(tree_data["out_nodes"],self.ui.scene)

    :notes: The data is generated from recurse of nodeUtils on graph saving.
    """

    if not tree_list:
        return

    for tnd in tree_list:
        if tnd["class"] != "widgets.ItemNode":
            continue

        _new_node = nodeUtils.getObject(tnd, scene_item)

        # create a new node if not in the scene and is unique
        if _new_node is None:
            _new_node = widgets.ItemNode(tnd["name"],
                                         tnd["x"],
                                         tnd["y"],
                                         scene_item,
                                         tnd["description"],
                                         tnd["uuid"])
            _new_node.command = tnd.get("command", "")

            # rebuild a node's in and out info
            if tnd["in_node"]:
                _nfo_in = getInfoDict(tnd["in_node"])
                _new_node.node_in = _nfo_in
            else:
                _new_node.node_in = None

            _tmp_out = list()
            for _on in tnd["out_nodes"]:
                _nfo_out = getInfoDict(_on)
                if _nfo_out:
                    _tmp_out.append(_nfo_out)

            _new_node.nodes_out = _tmp_out

            # icon
            _icon = tnd.get("icon", None)
            if not _icon or not os.path.exists(_icon):
                _new_node.changeIcon(config_obj.get("PATHS", "default_icon"))
            else:
                _new_node.changeIcon(_icon)

        # recurse
        buildTreeRecurse(tnd["out_nodes"], scene_item)


def linkTreeRecurse(tree_data, scene_item):
    """
    Reconnects all nodes in the dictionary.
    This is recursive

    **parameters**, **types**, **return** and **return types**

    :param tree_data: dictionary data parsed from JSON.
    :type tree_data: dict

    :param scene_item: Pointer of a QGraphicsScene object.
    :type scene_item: object

    :return: None
    :rtype: NoneType

    - Example::
        linkTreeRecurse(tree_data,self.ui.scene)

    :notes: The data is generated from the graph JSON file.
    """

    to_nodes = tree_data["out_nodes"]

    if not to_nodes:
        return

    nodeA = nodeUtils.getObject(tree_data, scene_item)
    if not nodeA:
        "Failed to find node - linkTreeRecurse"

    for tnd in to_nodes:
        nodeB = nodeUtils.getObject(tnd, scene_item)
        if not nodeB:
            "Destination node not found: {}".format(tnd.get("name", "Failed to get name"))

        new_wire = widgets.WireNode()
        new_wire.source = nodeA.plug_out
        new_wire.target = nodeB.plug_in
        new_wire.pointA = nodeA.plug_out.getCenter()
        new_wire.pointB = nodeB.plug_in.getCenter()

        nodeA.plug_out.out_wires.append(new_wire)
        nodeB.plug_in.in_wire = new_wire
        scene_item.addItem(new_wire)

        linkTreeRecurse(tnd, scene_item)


def alignTreeRecurse(node_obj):
    """
    Aligns all down-stream nodes of the specified node object.
    Will prevent covering other nodes but should be called 2x just in case.

    **parameters**, **types**, **return** and **return types**

    :param node_obj: Object pointer of a node.
    :type node_obj: object

    :return: None
    :rtype: NoneType

    - Example::

        alignTreeRecurse(self.starter)

    :notes: This is usually called 2x to prevent overlaps.
    """

    def update():
        node_obj.translate()
        node_obj.drawMe()

    if not isinstance(node_obj, widgets.ItemNode):
        return

    if not node_obj.plug_in:
        update()
        for _out_wire in node_obj.plug_out.out_wires:
            if not _out_wire.target:
                continue

            _target_parent = _out_wire.target.parentItem()
            alignTreeRecurse(_target_parent)
    else:
        if not node_obj.plug_in.in_wire:
            return

        in_p = node_obj.plug_in.in_wire.source.parentItem()
        in_p_targets = [w.target.parentItem() for w in in_p.plug_out.out_wires if w.target]
        p_index = in_p_targets.index(node_obj)

        node_obj.posX = in_p.posX + node_obj.width + 50
        node_obj.posY = in_p.posY + (120 * p_index)

        if node_obj.coveredBy():
            node_obj.posY += 120

        update()

        for _wire in node_obj.plug_out.out_wires:
            if not _wire.target:
                continue

            out_p = _wire.target.parentItem()
            alignTreeRecurse(out_p)


def write(file_path, data):
    """
    Saves a json file from the scene graph.
    Contents of json file must be generated from nodeUtils.recurse.
    Will create parent directories when not found.

    **parameters**, **types**, **return** and **return types**

    :param file_path: Full file path of the json file.
    :type file_path: str

    :param data: A valid, serializable dictionary.
    :type data: dict

    :return: If failed, returns None.
    :rtype: NoneType

    :return: Returns True if successful.
    :rtype: bool

    - Example::

        write(r"C:/temp/graph.json",graph_data)
    """

    file_root = os.path.dirname(file_path)

    if not os.path.exists(file_root):
        try:
            os.makedirs(file_root)
            print("Created new folder: {}".format(file_root))
        except Exception as err:
            print(str(err))
            print("Failed to create folder: {}".format(file_root))
            return

    try:
        with open(file_path, "w") as file_path:
            json.dump(data, file_path, indent=4)
    except Exception as err:
        print(str(err))
        return

    return True


def readGraphJson(file_path):
    """
    Reads a json file and returns its contents as a dict.
    Contents of json file must be generated from nodeUtils.recurse.
    Used for recreating a graph.

    **parameters**, **types**, **return** and **return types**

    :param file_path: Full file path of the json file.
    :type file_path: str

    :return: If failed, returns None.
    :rtype: NoneType

    :return: Returns a dict from the contents of "file_path".
    :rtype: dict

    - Example::

        readGraphJson(r"C:/temp/graph.json")
    """

    if not os.path.exists(file_path):
        print("No json file found: {}".format(file_path))
        return

    try:
        with open(file_path) as json_buffer:
            datas = json.load(json_buffer)
    except Exception as err:
        print(str(err))
        print("Failed to read: {}".format(file_path))
        return

    return datas


def getInfoDict(raw_dict):
    """
    Returns a dict with basic information for scene parsing.
    """

    if not isinstance(raw_dict, dict):
        return {}

    try:
        return {"name": raw_dict["name"],
                "uuid": uuid.UUID(raw_dict["uuid"])}
    except Exception as err:
        print(err)
        print(raw_dict)
        raise ValueError("Failed to build data from dict.")
