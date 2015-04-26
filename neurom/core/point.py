'''Point classes and functions'''

from collections import namedtuple
from neurom.core.dataformat import COLS

Point = namedtuple('Point', ('t', 'x', 'y', 'z', 'r'))


def point_from_row(row):
    '''Create a point from a data block row'''
    return Point(*row[COLS.TYPE: COLS.P])
