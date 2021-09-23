import maya.cmds as cmds
from traceback import print_exc


def main(data_block={}):
    """
    Opens a new Maya file.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Opening a new Maya scene...")

    try:
        cmds.file(new = True, f = True)
    except:
        print_exc()
        return

    cmds.refresh()
    return data_block