import maya.cmds as cmds


def main(data_block={}):
    """
    create a polygon cube.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Creating a cube named {}.".format(data_block["user"]))

    cmds.polyCube(n = data_block["user"])

    return data_block