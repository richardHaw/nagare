from __future__ import division
from __future__ import generators
from __future__ import print_function
# from __future__ import absolute_import
# from __future__ import unicode_literals

import os
import logging


def main(data_block={}):
    """
    Test for processing "what" in data_block.
    Return data_block
    """

    _log = logging.getLogger("nagare_log")
    _log.propagate = True
    _log.info(__name__)
    _log.info(data_block["what"])

    return data_block
