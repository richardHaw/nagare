import MaxPlus
from pymxs import runtime as rt


def main(data_block={}):
    """
    Saves the scene from data_block["scene"].

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Saving scene...")

    MaxPlus.FileManager.Reset(True)
    rt.redrawViews()

    return data_block
