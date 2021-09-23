from __future__ import division
from __future__ import generators
from __future__ import print_function
# from __future__ import absolute_import
#from __future__ import unicode_literals

import os, logging


def main(data_block={}):
    """
    Test for processing "where" in data_block.
    Return data_block
    """

    _log = logging.getLogger(os.environ["NAGARE_LOG"])
    _log.propagate = True
    _log.info(__name__)
    _log.info(data_block["where"])

    return data_block