from __future__ import print_function

import os, logging
from core import resultObj


def main(data_block={}):
    """
    Invoking an Error.
    Return None
    """

    _log = logging.getLogger(os.environ["NAGARE_LOG"])
    _log.propagate = True
    _log.info(__name__)
    _log.error("Simulating an Error")

    dummy_error = resultObj() # defaults to error

    dummy_error.addError({"item":"broken_node",
                          "type":"mesh",
                          "reason":"this is a dummy error1, example of full error"}
                         )

    dummy_error.addError({"item":"missing_object",
                          "reason":"you can just add item and no type or reason"}
                         )

    dummy_error.addError({"item":"no_type",
                          "reason":"this one has no type"}
                         )

    dummy_error.addError({"item":"item_only_specified"})

    dummy_error.addMessage("You can use the errors for selection, repair, etc")
    return dummy_error


if __name__ == "__main__":
    pass