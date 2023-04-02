from __future__ import division
from __future__ import generators
from __future__ import print_function
# from __future__ import absolute_import
# from __future__ import unicode_literals

import logging
from pprint import pformat
from app_py.configs import config_obj


def main(data_block={}):
    """
    Test for printing data_block.
    Return data_block
    """

    _log = logging.getLogger(config_obj.get("DETAILS", "log_name"))
    _log.propagate = True
    _log.debug(__name__)
    _log.debug(data_block)
    _log.debug(pformat(data_block, indent=4))

    return data_block
