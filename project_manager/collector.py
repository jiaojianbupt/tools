# -*- coding: utf-8 -*-
"""
"""
import os


GIT_FLAG = '.git'


def collect(path=None):
    if not path:
        path = os.getcwd()
    path = os.path.abspath(path)
    return find_directories(path)


def find_directories(path, results=None):
    if results is None:
        results = []
    for directory in os.listdir(path):
        full_path = os.path.join(path, directory)
        if os.path.isdir(full_path):
            results = find_directories(full_path, results)
    if GIT_FLAG in os.listdir(path) and os.path.isdir(os.path.join(path, GIT_FLAG)):
        results.append(path)
    return results


def main():
    print len(collect(path='/Users/jiaojian/repos'))


if __name__ == '__main__':
    main()
