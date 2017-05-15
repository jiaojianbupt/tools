# -*- coding: utf-8 -*-
"""
"""
import os
import sys
from manager import manage


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    manage()
