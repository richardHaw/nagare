import maya.cmds as cmds
from traceback import print_exc


def main(data_block={}):
    """
    Save a Maya file.
    requires data_block["new_file"]

    return data_block
    """

    _mf = data_block.get("new_file", "")
    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Saving: {}".format(_mf))

    try:
        cmds.file(rename=_mf)
        cmds.file(save=True, force=True)
    except:
        print_exc()
        return

    return data_block
