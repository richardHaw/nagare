import pymxs
rt = pymxs.runtime


def main(data_block={}):
    """
    create a teapot.

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Creating a teapot...")

    t = rt.Teapot()
    t.name = data_block["name"]
    data_block["teapot"] = t
    rt.redrawViews()

    return data_block