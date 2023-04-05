from __future__ import print_function

from app_py.resultObj import ResultObj
from app_py.utilities.logUtils import LOG_OBJ


def main(data_block={}):
    """
    Invoking an Error.
    Return None
    """

    LOG_OBJ.error("Simulating an Error")
    LOG_OBJ.error("Creating an error object...")

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
