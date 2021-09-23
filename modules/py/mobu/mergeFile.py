from pyfbsdk import FBSystem
from pyfbsdk import FBFbxOptions
from pyfbsdk import FBApplication

from traceback import print_exc


def main(data_block={}):
    """
    Merge a Motion Builder file into the current scene.

    requires data_block["motion_file"]

    return data_block
    """

    _mf = data_block.get("motion_file","")

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Opening: {}".format(_mf))

    try:
        options = FBFbxOptions(True)
        # options.NamespaceList = ns
        FBApplication().FileAppend(_mf,True,options)
    except:
        print_exc()
        return

    FBSystem().Spawn.Evaluate()

    return data_block