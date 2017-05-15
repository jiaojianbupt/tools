# -*- coding: utf-8 -*-
"""
"""
import sys
import logging


class ConsoleColor(object):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


class LogLevel(object):
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    ERROR = 'ERROR'
    FATAL = 'FATAL'


def print_with_style(text, color=None, prefix=None, new_line=True, next_line=False, write_log=False):
    if prefix is None:
        prefix = 'INFO'
    if prefix == '':
        text = '%s' % text
    else:
        text = '%s: %s' % (prefix, text)
    if color:
        text = '\x1b[1;%dm%s\x1b[0m' % ((30+color), text)
    if next_line:
        text = '\n' + text
    if new_line:
        sys.stdout.write(text + '\n')
    else:
        sys.stdout.write(text + '\r')
    if write_log:
        getattr(logging, prefix.lower())(text)
    sys.stdout.flush()
