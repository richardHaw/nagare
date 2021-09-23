import MaxPlus


def main(data_block={}):
    """
    Saves the scene from data_block["scene"].

    return data_block
    """

    _log = data_block["logger"]
    _log.write(__name__)
    _log.write("Saving scene...")

    MaxPlus.FileManager.Save(data_block["scene"])
    _log.write("Saved: {}".format(data_block["scene"]))

    return data_block