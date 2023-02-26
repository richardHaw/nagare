from pymxs import runtime as rt


def main(data_block={}):
    """
    create a biped.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Creating a biped...")

    bipObj = rt.biped.createNew(100, 100, rt.point3(0, 0, 50))
    rt.redrawViews()
    _log.write("New biped creatd...")

    return data_block
