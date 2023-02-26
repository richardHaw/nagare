import pymxs
rt = pymxs.runtime


def main(data_block={}):
    """
    Bends the teapot from data_block.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Adding Bend modifier to teapot...")

    t = data_block["teapot"]
    mod = rt.bend()
    mod.BendAngle = -27.0
    mod.BendDir = -90.0
    rt.addModifier(t, mod)
    rt.redrawViews()

    return data_block
