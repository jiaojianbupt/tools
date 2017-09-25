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


def get_max_repr_length(targets):
    max_length = 0
    for t in targets:
        if len(str(t)) > max_length:
            max_length = len(str(t))
    return max_length


def print_as_table(rows, split_first=True):
    max_length_dict = {}
    for elements in rows:
        for element_index, element in enumerate(elements):
            max_length = max_length_dict.get(element_index, 0)
            current_length = len(str(element))
            if current_length > max_length:
                max_length_dict[element_index] = current_length

    text_parts = []
    left_border = '| '
    right_border = ' |'
    splitter = ' | '
    line_splitter = '+%s+' % '+'.join([''.center(max_length_dict[i] + 2, '-') for i in range(len(max_length_dict))])

    text_parts.append(line_splitter)
    for row_index, elements in enumerate(rows):
        text_part = left_border
        for element_index, element in enumerate(elements[:-1]):
            text_part += str(element).ljust(max_length_dict[element_index]) + splitter

        text_part += str(elements[-1]).ljust(max_length_dict[len(elements) - 1]) + right_border
        text_parts.append(text_part)
        if split_first and row_index == 0:
            text_parts.append(line_splitter)
    text_parts.append(line_splitter)
    return '\n'.join(text_parts)
