# -*- coding: utf-8 -*-
"""
"""
from tools.utils.basic_printer import print_with_style, LogLevel, ConsoleColor


class ProgressMonitor(object):

    def __init__(self, counter, total, max_path_length):
        self.counter = counter
        self.total = total
        self.max_path_length = max_path_length

    def increment(self, result):
        self.counter.increment()
        self.update_display_text(result.path, result.cost)

    def update_display_text(self, path, cost, too_slow=False):
        path = path.ljust(self.max_path_length)
        progress_text = 'progress: %s/%s' % (self.counter.get_value(), self.total)
        if too_slow:
            text = '%s, still processing %s. ' % (progress_text, path)
        else:
            text = '%s, %s finished in %.2f seconds. ' % (progress_text, path, cost)
        text = text.ljust(120)
        print_with_style(text, color=ConsoleColor.GREEN,
                         new_line=False, prefix=LogLevel.INFO)
