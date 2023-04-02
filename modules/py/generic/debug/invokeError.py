from __future__ import print_function

import logging
from app_py.resultObj import ResultObj
from app_py.configs import config_obj


def main(data_block={}):
    """
    Invoking an Error.
    Return None
    """

    _log = logging.getLogger(config_obj.get("DETAILS", "log_name"))
    _log.propagate = True
    _log.info(__name__)
    _log.error("Simulating an Error")

    dummy_error = ResultObj()  # defaults to error

    dummy_error.addError({"item": "broken_node",
                          "type": "mesh",
                          "reason": "this is a dummy error1, example of full error"}
                         )

    dummy_error.addError({"item": "missing_object",
                          "reason": "you can just add item and no type or reason"}
                         )

    dummy_error.addError({"item": "no_type",
                          "reason": "this one has no type"}
                         )

    dummy_error.addError({"item": "item_only_specified"})

    dummy_error.addMessage("You can use the errors for selection, repair, etc")
    return dummy_error
