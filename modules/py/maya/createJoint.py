import maya.cmds as cmds


def main(data_block={}):
    """
    create a Joint.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Creating a joinnt...")

    cmds.select(cl = True)
    cmds.joint()

    return data_block