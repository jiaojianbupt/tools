# -*- coding: utf-8 -*-
"""
Created by jiaojian at 2017/12/3 20:10
"""
import os


def read_from_file(directory, recursive=True):
    results = {}
    file_paths = os.listdir(directory)
    for path in file_paths:
        if os.path.isdir(path):
            if recursive:
                results.update(read_from_file(path, recursive=recursive))
            else:
                continue
        else:
            with open(os.path.join(directory, path), 'r') as conf_file:
                for line in conf_file.readlines():
                    fields = line.split(' ')
                    if len(fields) != 2:
                        continue
                    if not fields[0] or not fields[1]:
                        continue
                    if fields[0] in results:
                        print 'Duplicated key %s in %s' % (fields[0], path)
                    results[fields[0]] = fields[1]
    return results


if __name__ == '__main__':
    print read_from_file('/Users/jiaojian/repos/ss_conf_aws/ss')
