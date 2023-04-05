from __future__ import print_function

from app_py.resultObj import ResultObj
from app_py.utilities.logUtils import LOG_OBJ


def main(data_block={}):
    """
    Invoking Skip so down-stream graph won't be calculated

    Return "skip"
    """

    LOG_OBJ.warning("Simulating a skip...")

    skip_obj = ResultObj("skip")
    skip_obj.addMessage("This is an example skip node...")

    return skip_obj
