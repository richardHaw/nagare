import maya.cmds as cmds


def main(data_block={}):
    """
    create a sphere.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Creating a sphere...")
    cmds.sphere(radius=5)

    return data_block
