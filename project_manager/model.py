# -*- coding: utf-8 -*-
"""
"""
from tools.utils.printer import print_with_style, LogLevel, ConsoleColor


class ProgressMonitor(object):

    def __init__(self, counter, total):
        self.counter = counter
        self.total = total

    def increment(self, result):
        self.counter.increment()
        self.update_display_text(result)

    def update_display_text(self, result):
        text = 'progress: %s/%s, %s finished in %s seconds.' % (self.counter.get_value(), self.total, result.path, result.cost)
        print_with_style(text, color=ConsoleColor.GREEN,
                         new_line=False, prefix=LogLevel.INFO)
