# -*- coding: utf-8 -*-
"""
"""
import argparse
import os
import multiprocessing
from collector import collect
from command import update


STATUS_FAILED = 256
TIMEOUT_MESSAGE = 'timeout.'
STATUS_UNKNOWN = 256
UNKNOWN_ERROR_TEMPLATE = 'Unknown exception: %s.'


def prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, help='Target directory.')
    parser.add_argument('-c', '--clean-dirty', action='store_true', help='Clean dirty changes.')
    parser.add_argument('-u', '--update-code', action='store_true', help='Update your code by "git pull -r".')
    parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout for update single repository.')
    args = parser.parse_args()
    return args


def main():
    args = prepare_args()
    directories = collect(path='/home/jiaojian/repos')
    async_results = {}
    success_repos = {}
    failed_repos = {}
    process_pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for directory in directories:
        print 'updating %s' % os.path.basename(directory)
        async_results[directory] = process_pool.apply_async(update, args=(directory, args.clean_dirty))
    for directory in async_results:
        try:
            status, message = async_results[directory].get(timeout=args.timeout)
        except multiprocessing.TimeoutError:
            status, message = STATUS_FAILED, TIMEOUT_MESSAGE
        except Exception as e:
            status, message = STATUS_UNKNOWN, UNKNOWN_ERROR_TEMPLATE % e.message
        if status:
            failed_repos[directory] = message
        else:
            success_repos[directory] = message
    print '%s/%s updated.' % (len(success_repos), len(directories))
    for directory in failed_repos:
        print '%s: %s\n%s' % (os.path.basename(directory), directory, failed_repos[directory])


if __name__ == '__main__':
    main()
