# -*- coding: utf-8 -*-
"""
"""
from s3_client import S3ObjectSequence
from utils import timer


DEFAULT_BRANCHES = 10
NOT_FOUND = -1


class CompareType(object):
    GE = 0
    LE = 1
    LT = 2
    GT = 3


@timer(times=100)
def n_search(n, target_value, target_collection, start=None, end=None, compare_type=None):
    if n < 2:
        n = DEFAULT_BRANCHES
    if start is None:
        start = 0
    if end is None:
        end = len(target_collection) - 1
    if compare_type is None:
        compare_type = CompareType.GE
    result = _n_search(n, target_value, target_collection, start, end, compare_type)
    target_collection.clear_cache()
    return result


def _n_search(n, target_value, target_collection, start, end, compare_type):

    if end - start < n:
        if compare_type == CompareType.GE:
            if target_collection[end] < target_value:
                return NOT_FOUND
            if target_collection[start] >= target_value:
                return start
            for j, value in enumerate(target_collection[start:end + 1]):
                if value >= target_value:
                    return start + j
        elif compare_type == CompareType.LE:
            if target_collection[start] > target_value:
                return NOT_FOUND
            if target_collection[end] <= target_value:
                return end
            for j, value in enumerate(target_collection[start:end + 1]):
                if value > target_value:
                    return start + j - 1
    else:
        check_points = _get_check_points(start, end, n)
        if isinstance(target_collection, S3ObjectSequence):
            target_collection.prepare(check_points)
        if compare_type == CompareType.GE:
            if target_collection[check_points[-1]] < target_value:
                return NOT_FOUND
            if target_collection[check_points[0]] >= target_value:
                return 0
            left_check_point = check_points[0]
            for check_point in check_points[1:]:
                if target_collection[left_check_point] == target_collection[check_point]:
                    left_check_point = check_point
                    continue
                if target_collection[left_check_point] < target_value <= target_collection[check_point]:
                    return _n_search(n, target_value, target_collection, left_check_point, check_point, compare_type)
                left_check_point = check_point
        elif compare_type == CompareType.LE:
            if target_collection[check_points[0]] > target_value:
                return NOT_FOUND
            if target_collection[check_points[-1]] <= target_value:
                return len(target_collection) - 1
            left_check_point = check_points[0]
            for check_point in check_points[1:]:
                if target_collection[left_check_point] == target_collection[check_point]:
                    left_check_point = check_point
                    continue
                if target_collection[left_check_point] <= target_value < target_collection[check_point]:
                    return _n_search(n, target_value, target_collection, left_check_point, check_point, compare_type)
                left_check_point = check_point


def _get_check_points(start, end, n):
    distance = (end - start) / n
    check_points = []
    for i in range(n):
        check_points.append(start + i * distance)
    check_points.append(end)
    return check_points


def main():
    s3_file = S3ObjectSequence('bytedance-root', 'user/wudi/event_param_test_4_20170101_compact6.sort2.bin', 12)
    target_collection = [3 for i in range(40000)]
    for _ in range(100):
        target_collection.insert(0, 1)
    n_search(2, 6362894245031707139, s3_file, compare_type=CompareType.GE)
    for n in range(2, 20):
        print n, n_search(n, 6362894245031707139, s3_file, compare_type=CompareType.GE)


if __name__ == '__main__':
    main()
