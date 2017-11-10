# -*- coding: utf-8 -*-
"""
"""
from tools.utils.printer import print_with_style, LogLevel, ConsoleColor


class ProgressMonitor(object):

    def __init__(self, counter, total, max_path_length):
        self.counter = counter
        self.total = total
        self.max_path_length = max_path_length

    def increment(self, result):
        self.counter.increment()
        self.update_display_text(result)

    def update_display_text(self, result):
        path = result.path.ljust(self.max_path_length)
        text = 'progress: %s/%s, %s finished in %.2f seconds.' % (self.counter.get_value(), self.total, path, result.cost)
        print_with_style(text, color=ConsoleColor.GREEN,
                         new_line=False, prefix=LogLevel.INFO)
