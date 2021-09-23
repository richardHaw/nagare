from pyfbsdk import FBSystem
from pyfbsdk import FBFbxOptions
from pyfbsdk import FBApplication
from pyfbsdk import FBCharacterInputType

from traceback import format_exc


def main(data_block={}):
    """
    Changes the source of A to B.

    requires data_block["source_ch"]
    requires data_block["target_ch"]

    return data_block
    """

    _source_name = data_block.get("source_ch","")
    _target_name = data_block.get("target_ch","")

    _log = data_block["logger"]
    _log.write(__name__)

    _source_node = ""
    _terget_node = ""

    try:
        for _ch in FBSystem().Spawn.Characters:
            if _ch.LongName == _source_name:
                _source_node = _ch
            elif _ch.LongName == _target_name:
                _terget_node = _ch

        _terget_node.InputCharacter = _source_node
        _terget_node.InputType = FBCharacterInputType.kFBCharacterInputCharacter
        _terget_node.Active = True
    except:
        _log.write(format_exc())
        return

    FBSystem().Spawn.Evaluate()

    return data_block