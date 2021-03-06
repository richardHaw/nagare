from __future__ import print_function

import os, logging
from core import resultObj


def main(data_block={}):
    """
    Invoking Skip so down-stream graph won't be calculated

    Return "skip"
    """

    _log = logging.getLogger(os.environ["NAGARE_LOG"])
    _log.propagate = True
    _log.info(__name__)
    _log.warning("Simulating a skip...")

    skip_obj = resultObj("skip")
    skip_obj.addMessage("This is an example skip node...")

    return skip_obj