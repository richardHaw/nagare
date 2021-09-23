import maya.cmds as cmds


def main(data_block={}):
    """
    create a Camera.
    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Creating a camera...")

    cmds.select(cl = True)
    cmds.camera()

    return data_block