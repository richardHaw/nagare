from __future__ import division
from __future__ import generators
from __future__ import print_function
# from __future__ import absolute_import
#from __future__ import unicode_literals

import os
import logging
from pprint import pformat


def main(data_block={}):
    """
    Prints data_block.
    Return data_block
    """

    _log = logging.getLogger("nagare_log")
    _log.propagate = True
    _log.info(__name__)
    _log.info(pformat(data_block,indent=4))

    return data_block
