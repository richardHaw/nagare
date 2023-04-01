from __future__ import division
from __future__ import generators
from __future__ import print_function
# from __future__ import absolute_import
# from __future__ import unicode_literals

import os
import logging


def main(data_block={}):
    """
    Test for changing "why" value in data_block.
    Return data_block
    """

    data_block["why"] = "Helping people bring out the best in themselves."

    _log = logging.getLogger("nagare_log")
    _log.propagate = True
    _log.info(__name__)
    _log.info(data_block["why"])

    return data_block
