# -*- coding: utf-8 -*-
"""
"""
import multiprocessing


class SafeCounter(object):

    def __init__(self, counter=None, lock=None):
        if not counter:
            self.counter = multiprocessing.Value('i', 0)
        if not lock:
            self.lock = multiprocessing.Lock()

    def increment(self, step=1):
        with self.lock:
            self.counter.value += step

    def get_value(self):
        return self.counter.value