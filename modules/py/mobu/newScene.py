from pyfbsdk import FBSystem
from pyfbsdk import FBApplication

from traceback import print_exc


def main(data_block={}):
    """
    Open a new scene.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Opening a new scene...")

    try:
        FBApplication().FileNew()
    except:
        print_exc()
        return

    FBSystem().Spawn.Evaluate()

    return data_block