import maya.cmds as cmds
from traceback import print_exc


def main(data_block={}):
    """
    Open a Maya file.

    requires data_block["maya_file"]

    return data_block
    """

    _mf = data_block.get("maya_file", "")

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Opening: {}".format(_mf))

    try:
        cmds.file(_mf, open=True, force=True)
    except:
        print_exc()
        return

    cmds.refresh()
    return data_block
