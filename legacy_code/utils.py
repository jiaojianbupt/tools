# -*- coding: utf-8 -*-
"""
"""
import time


def timer(times=5):
    def _timer(func):
        def __timer(*args, **kwargs):
            total_time_cost = 0
            max_time = 0
            min_time = 0
            result = None
            for i in range(times):
                start_time = time.time()
                result = func(*args, **kwargs)
                time_cost = ((time.time() - start_time) * 1000)
                total_time_cost += time_cost
                if time_cost > max_time:
                    max_time = time_cost
                if i == 0:
                    min_time = time_cost
                else:
                    if min_time > time_cost:
                        min_time = time_cost
            print 'avg %.2fms, max %.2fms, min %.2fms' % (float(total_time_cost)/times, max_time, min_time)
            return result
        return __timer
    return _timer
