# -*- coding: utf-8 -*-
"""
"""
from tools.utils.printer import print_with_style, LogLevel, ConsoleColor


class ProgressMonitor(object):

    def __init__(self, counter, total):
        self.counter = counter
        self.total = total

    def increment(self, *args, **kwargs):
        _, _ = args, kwargs
        self.counter.increment()
        self.update_display_text()

    def update_display_text(self):
        print_with_style('progress: %s/%s' % (self.counter.get_value(), self.total), color=ConsoleColor.GREEN,
                         new_line=False, prefix=LogLevel.INFO)
