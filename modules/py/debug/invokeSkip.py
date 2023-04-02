from __future__ import print_function

import logging
from app_py.resultObj import ResultObj
from app_py.configs import config_obj


def main(data_block={}):
    """
    Invoking Skip so down-stream graph won't be calculated

    Return "skip"
    """

    _log = logging.getLogger(config_obj.get("DETAILS", "log_name"))
    _log.propagate = True
    _log.info(__name__)
    _log.warning("Simulating a skip...")

    skip_obj = ResultObj("skip")
    skip_obj.addMessage("This is an example skip node...")

    return skip_obj
