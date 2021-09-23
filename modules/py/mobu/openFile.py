from pyfbsdk import FBSystem
from pyfbsdk import FBApplication

from traceback import print_exc


def main(data_block={}):
    """
    Open a Motion Builder file.

    requires data_block["mobu_file"]

    return data_block
    """

    _mf = data_block.get("mobu_file","")

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Opening: {}".format(_mf))

    try:
        FBApplication().FileOpen(_mf)
    except:
        print_exc()
        return

    FBSystem().Spawn.Evaluate()

    return data_block