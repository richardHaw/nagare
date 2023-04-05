from __future__ import division
from __future__ import generators
from __future__ import print_function
# from __future__ import absolute_import
# from __future__ import unicode_literals

from pprint import pformat
from app_py.utilities.logUtils import LOG_OBJ


def main(data_block={}):
    """
    Test for printing data_block.
    Return data_block
    """

    LOG_OBJ.debug(pformat(data_block, indent=4))

    return data_block
